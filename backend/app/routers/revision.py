import datetime
import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.test import Test, Question, QuestionOption
from app.models.revision import TopicMastery, MistakeNotebook, Flashcard
from app.schemas.revision import (
    TopicMasteryOut, WeaknessAnalysisResponse, WeaknessConcept,
    MistakeItemOut, ResolveMistakeRequest, FlashcardOut,
    FlashcardCreateRequest, FlashcardReviewRequest, DailyPlanOut
)
from app.schemas.test import TestDetailOut, QuestionOut, OptionOut
from app.services.revision_service import calculate_sm2_interval
from app.services.ai_generator import synthesize_grounded_questions
from app.dependencies import get_current_user

router = APIRouter(prefix="/revision", tags=["Adaptive Revision & Weakness Forge"])

@router.get("/weaknesses", response_model=WeaknessAnalysisResponse)
def get_weakness_analysis(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user.id
    records = db.query(TopicMastery).filter(TopicMastery.user_id == user_id).all()

    weak = []
    moderate = []
    strong = []

    for r in records:
        concept = WeaknessConcept(
            topic=r.topic,
            subject=r.subject or "General",
            accuracy_rate=r.accuracy_rate,
            total_attempted=r.total_attempted,
            recommended_focus="High-frequency conceptual misconceptions and definitions",
            suggested_revision_action="Review primary document section and take a 5-question targeted adaptive quiz"
        )
        if r.accuracy_rate < 60.0:
            weak.append(concept)
        elif r.accuracy_rate < 80.0:
            moderate.append(concept)
        else:
            strong.append(concept)

    avg_mastery = round(sum(r.accuracy_rate for r in records) / len(records), 1) if records else 0.0

    return WeaknessAnalysisResponse(
        overall_mastery_score=avg_mastery,
        weakest_topics=weak,
        moderate_topics=moderate,
        strong_topics=strong,
        recommended_study_hours=max(1.0, round(len(weak) * 0.75, 1))
    )

@router.post("/forge-test", response_model=TestDetailOut)
def forge_adaptive_test(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    1-Click 'Forge My Weaknesses' Engine:
    Identifies topics with lowest accuracy, pulls grounded document chunks,
    and synthesizes a targeted adaptive practice exam.
    """
    user_id = current_user.id
    weak_records = db.query(TopicMastery).filter(
        TopicMastery.user_id == user_id
    ).order_by(TopicMastery.accuracy_rate.asc()).limit(3).all()

    target_topic = weak_records[0].topic if weak_records else None

    # Find student documents
    user_docs = db.query(Document).filter(
        Document.user_id == user_id,
        Document.processing_status == "completed"
    ).all()
    if not user_docs:
        raise HTTPException(status_code=400, detail="No processed study materials found to forge a test.")

    chunks_list = []
    for doc in user_docs:
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

    existing_tests = db.query(Test).filter(Test.user_id == user_id).all()
    existing_q_texts = []
    if existing_tests:
        test_ids = [t.id for t in existing_tests]
        prev_qs = db.query(Question.question_text).filter(Question.test_id.in_(test_ids)).all()
        existing_q_texts = [q[0] for q in prev_qs]

    raw_questions = synthesize_grounded_questions(
        chunks=chunks_list,
        requested_count=5,
        difficulty="medium",
        topic_filter=target_topic,
        question_types=["mcq"],
        document_id=user_docs[0].id,
        document_title=user_docs[0].title,
        existing_question_texts=existing_q_texts
    )

    test_title = f"Adaptive Forge: {target_topic or 'Targeted Review'}"
    new_test = Test(
        user_id=user_id,
        document_ids=json.dumps([d.id for d in user_docs]),
        title=test_title,
        subject="Adaptive Weakness Forge",
        topic=target_topic or "Targeted Revision",
        test_type="revision",
        difficulty="medium",
        total_questions=len(raw_questions),
        time_limit_minutes=10,
        negative_marking=False,
        passing_percentage=70.0
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    created_questions_out = []
    for idx, q_data in enumerate(raw_questions):
        q_record = Question(
            test_id=new_test.id,
            order_index=idx,
            question_text=q_data["question_text"],
            question_type=q_data.get("question_type", "mcq"),
            difficulty=q_data.get("difficulty", "medium"),
            topic_tag=q_data.get("topic_tag", target_topic or "General"),
            marks=1.0,
            source_document_id=q_data.get("source_document_id"),
            source_document_title=q_data.get("source_document_title"),
            source_page=q_data.get("source_page"),
            source_passage_snippet=q_data.get("source_passage_snippet"),
            explanation_text=q_data["explanation"]
        )
        db.add(q_record)
        db.commit()
        db.refresh(q_record)

        opts_out = []
        for opt in q_data.get("options", []):
            opt_rec = QuestionOption(
                question_id=q_record.id,
                option_key=opt["key"],
                option_text=opt["text"],
                is_correct=opt.get("is_correct", False)
            )
            db.add(opt_rec)
            db.commit()
            db.refresh(opt_rec)
            opts_out.append(OptionOut(id=opt_rec.id, option_key=opt_rec.option_key, option_text=opt_rec.option_text))

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
            options=opts_out
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

@router.get("/mistakes", response_model=List[MistakeItemOut])
def get_mistake_notebook(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mistakes = db.query(MistakeNotebook).filter(
        MistakeNotebook.user_id == current_user.id
    ).order_by(MistakeNotebook.is_resolved.asc(), MistakeNotebook.added_at.desc()).all()
    return mistakes

@router.put("/mistakes/{mistake_id}/resolve")
def resolve_mistake(
    mistake_id: int,
    req: ResolveMistakeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mistake = db.query(MistakeNotebook).filter(
        MistakeNotebook.id == mistake_id,
        MistakeNotebook.user_id == current_user.id
    ).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="Mistake notebook entry not found")

    mistake.is_resolved = req.is_resolved
    mistake.reviewed_count += 1
    db.commit()
    return {"message": "Mistake status updated", "is_resolved": mistake.is_resolved}

@router.get("/flashcards", response_model=List[FlashcardOut])
def get_flashcards(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cards = db.query(Flashcard).filter(
        Flashcard.user_id == current_user.id
    ).order_by(Flashcard.next_review_date.asc()).all()
    return cards

@router.post("/flashcards", response_model=FlashcardOut)
def create_flashcard(
    req: FlashcardCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = Flashcard(
        user_id=current_user.id,
        document_id=req.document_id,
        topic=req.topic,
        front_prompt=req.front_prompt,
        back_explanation=req.back_explanation,
        difficulty=req.difficulty or "medium",
        next_review_date=datetime.date.today()
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

@router.post("/flashcards/{flashcard_id}/review")
def review_flashcard(
    flashcard_id: int,
    req: FlashcardReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card = db.query(Flashcard).filter(
        Flashcard.id == flashcard_id,
        Flashcard.user_id == current_user.id
    ).first()
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    new_reps, new_interval, new_ef = calculate_sm2_interval(
        rating=req.rating,
        repetitions=card.repetition_count,
        ease_factor=card.ease_factor,
        interval_days=card.interval_days
    )

    card.repetition_count = new_reps
    card.interval_days = new_interval
    card.ease_factor = new_ef
    card.next_review_date = datetime.date.today() + datetime.timedelta(days=new_interval)
    db.commit()

    return {
        "message": "Flashcard scheduled",
        "next_review_date": card.next_review_date.isoformat(),
        "interval_days": new_interval,
        "repetitions": new_reps
    }

@router.get("/daily-plan", response_model=DailyPlanOut)
def get_daily_plan(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user.id
    today = datetime.date.today()

    due_cards = db.query(Flashcard).filter(
        Flashcard.user_id == user_id,
        Flashcard.next_review_date <= today
    ).count()

    unresolved_mistakes = db.query(MistakeNotebook).filter(
        MistakeNotebook.user_id == user_id,
        MistakeNotebook.is_resolved == False
    ).count()

    weakest = db.query(TopicMastery).filter(
        TopicMastery.user_id == user_id
    ).order_by(TopicMastery.accuracy_rate.asc()).first()

    primary_topic = weakest.topic if weakest else "Core Syllabus Review"

    actions = [
        {"title": f"Review {due_cards} Spaced-Repetition Flashcards", "type": "flashcards", "estimated_mins": max(5, due_cards * 1)},
        {"title": f"Tackle {unresolved_mistakes} Logged Mistakes in Notebook", "type": "mistakes", "estimated_mins": max(5, unresolved_mistakes * 2)},
        {"title": f"Forge Weakness Test: {primary_topic}", "type": "forge_test", "estimated_mins": 10}
    ]

    return DailyPlanOut(
        today_date=today.strftime("%A, %B %d"),
        greeting=f"Welcome back, {current_user.full_name.split()[0]}!",
        target_study_minutes=current_user.profile.daily_goal_minutes if current_user.profile else 45,
        streak_count=current_user.profile.current_streak if current_user.profile else 1,
        due_flashcards_count=due_cards,
        unresolved_mistakes_count=unresolved_mistakes,
        primary_revision_topic=primary_topic,
        recommended_actions=actions
    )
