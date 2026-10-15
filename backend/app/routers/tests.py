import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.test import Test, Question, QuestionOption
from app.schemas.test import (
    GenerateTestRequest, TestOut, TestDetailOut, QuestionOut, OptionOut,
    ExamBlueprintRequest, ExamBlueprintResponse
)
from app.services.ai_generator import synthesize_grounded_questions, generate_exam_blueprint
from app.dependencies import get_current_user

router = APIRouter(prefix="/tests", tags=["AI Question Generation & Test Configuration"])

@router.post("/generate", response_model=TestDetailOut)
def generate_test(req: GenerateTestRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.document_ids:
        raise HTTPException(status_code=400, detail="At least one source document must be selected")

    # Verify document ownership
    docs = db.query(Document).filter(
        Document.id.in_(req.document_ids),
        Document.user_id == current_user.id
    ).all()
    if not docs:
        raise HTTPException(status_code=404, detail="Selected study materials not found or unauthorized")

    # Gather chunks
    chunks_list = []
    first_doc_title = docs[0].title
    for doc in docs:
        doc_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        for dc in doc_chunks:
            chunks_list.append({
                "chunk_index": dc.chunk_index,
                "page_number": dc.page_number,
                "section_heading": dc.section_heading,
                "content": dc.content,
                "token_count": dc.token_count,
                "document_id": doc.id,
                "document_title": doc.title
            })

    if not chunks_list:
        raise HTTPException(
            status_code=400,
            detail="The selected document(s) have not finished processing yet or contain no extractable text."
        )

    # Fetch existing questions for this user to ensure fresh, non-repeating questions
    existing_tests = db.query(Test).filter(Test.user_id == current_user.id).all()
    existing_q_texts = []
    if existing_tests:
        test_ids = [t.id for t in existing_tests]
        prev_qs = db.query(Question.question_text).filter(Question.test_id.in_(test_ids)).all()
        existing_q_texts = [q[0] for q in prev_qs]

    # Synthesize questions
    raw_questions = synthesize_grounded_questions(
        chunks=chunks_list,
        requested_count=req.question_count,
        difficulty=req.difficulty,
        topic_filter=req.topic,
        question_types=req.question_types,
        document_id=docs[0].id,
        document_title=docs[0].title,
        existing_question_texts=existing_q_texts
    )

    if not raw_questions:
        raise HTTPException(
            status_code=400,
            detail="Could not generate questions from the selected material. Please ensure the document contains sufficient technical content."
        )

    test_title = req.title.strip() if req.title and req.title.strip() else f"Assessment: {first_doc_title}"

    # Create Test record
    new_test = Test(
        user_id=current_user.id,
        document_ids=json.dumps(req.document_ids),
        title=test_title,
        subject=req.subject or "Computer Science",
        topic=req.topic or "Comprehensive",
        test_type=req.test_type,
        difficulty=req.difficulty,
        total_questions=len(raw_questions),
        time_limit_minutes=req.time_limit_minutes,
        negative_marking=req.negative_marking,
        negative_mark_value=req.negative_mark_value,
        passing_percentage=60.0
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    # Create Questions & Options
    created_questions_out = []
    for idx, q_data in enumerate(raw_questions):
        q_record = Question(
            test_id=new_test.id,
            order_index=idx,
            question_text=q_data["question_text"],
            question_type=q_data.get("question_type", "mcq"),
            difficulty=q_data.get("difficulty", req.difficulty),
            topic_tag=q_data.get("topic_tag", "General"),
            marks=q_data.get("marks", 1.0),
            source_document_id=q_data.get("source_document_id"),
            source_document_title=q_data.get("source_document_title"),
            source_page=q_data.get("source_page"),
            source_passage_snippet=q_data.get("source_passage_snippet"),
            explanation_text=q_data["explanation"]
        )
        db.add(q_record)
        db.commit()
        db.refresh(q_record)

        options_out = []
        for opt in q_data.get("options", []):
            opt_record = QuestionOption(
                question_id=q_record.id,
                option_key=opt["key"],
                option_text=opt["text"],
                is_correct=opt.get("is_correct", False)
            )
            db.add(opt_record)
            db.commit()
            db.refresh(opt_record)
            # Hide correct answer from return payload during test creation
            options_out.append(OptionOut(id=opt_record.id, option_key=opt_record.option_key, option_text=opt_record.option_text))

        created_questions_out.append(QuestionOut(
            id=q_record.id,
            order_index=q_record.order_index,
            question_text=q_record.question_text,
            question_type=q_record.question_type,
            difficulty=q_record.difficulty,
            topic_tag=q_record.topic_tag,
            marks=q_record.marks,
            source_document_id=q_record.source_document_id,
            source_document_title=q_record.source_document_title,
            source_page=q_record.source_page,
            source_passage_snippet=q_record.source_passage_snippet,
            options=options_out
        ))

    return TestDetailOut(
        id=new_test.id,
        user_id=new_test.user_id,
        title=new_test.title,
        subject=new_test.subject,
        topic=new_test.topic,
        test_type=new_test.test_type,
        difficulty=new_test.difficulty,
        total_questions=new_test.total_questions,
        time_limit_minutes=new_test.time_limit_minutes,
        negative_marking=new_test.negative_marking,
        negative_mark_value=new_test.negative_mark_value,
        passing_percentage=new_test.passing_percentage,
        created_at=new_test.created_at,
        questions=created_questions_out
    )

@router.get("", response_model=List[TestOut])
def list_tests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tests = db.query(Test).filter(
        Test.user_id == current_user.id
    ).order_by(Test.created_at.desc()).all()
    return tests

@router.get("/{test_id}", response_model=TestDetailOut)
def get_test_detail(test_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    test = db.query(Test).filter(
        Test.id == test_id,
        Test.user_id == current_user.id
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    questions_out = []
    for q in test.questions:
        opts_out = [OptionOut(id=o.id, option_key=o.option_key, option_text=o.option_text) for o in q.options]
        questions_out.append(QuestionOut(
            id=q.id,
            order_index=q.order_index,
            question_text=q.question_text,
            question_type=q.question_type,
            difficulty=q.difficulty,
            topic_tag=q.topic_tag,
            marks=q.marks,
            source_document_id=q.source_document_id,
            source_document_title=q.source_document_title,
            source_page=q.source_page,
            source_passage_snippet=q.source_passage_snippet,
            options=opts_out
        ))

    return TestDetailOut(
        id=test.id,
        user_id=test.user_id,
        title=test.title,
        subject=test.subject,
        topic=test.topic,
        test_type=test.test_type,
        difficulty=test.difficulty,
        total_questions=test.total_questions,
        time_limit_minutes=test.time_limit_minutes,
        negative_marking=test.negative_marking,
        negative_mark_value=test.negative_mark_value,
        passing_percentage=test.passing_percentage,
        created_at=test.created_at,
        questions=questions_out
    )

@router.post("/blueprint", response_model=ExamBlueprintResponse)
def get_exam_blueprint_plan(req: ExamBlueprintRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(
        Document.id.in_(req.document_ids),
        Document.user_id == current_user.id
    ).all()
    if not docs:
        raise HTTPException(status_code=404, detail="Documents not found")

    chunks_list = []
    for doc in docs:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        for c in chunks:
            chunks_list.append({
                "chunk_index": c.chunk_index,
                "page_number": c.page_number,
                "section_heading": c.section_heading,
                "content": c.content
            })

    blueprint = generate_exam_blueprint(
        chunks=chunks_list,
        document_title=docs[0].title,
        total_questions=req.total_questions,
        target_difficulty=req.target_difficulty
    )
    return blueprint
