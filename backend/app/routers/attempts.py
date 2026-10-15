import datetime
import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.test import Test, Question, QuestionOption
from app.models.attempt import TestAttempt, StudentResponse
from app.schemas.test import QuestionOut, OptionOut
from app.schemas.attempt import (
    StartAttemptResponse, AnswerSaveRequest, AnswerSaveResponse,
    SubmitAttemptRequest, AttemptResultResponse, QuestionResultDetail
)
from app.services.exam_service import evaluate_and_grade_attempt
from app.services.feedback_coach import generate_detailed_mistake_feedback, generate_attempt_summary_and_plan
from app.services.revision_service import update_topic_mastery_from_attempt
from app.dependencies import get_current_user

router = APIRouter(tags=["Exam Arena & Attempts"])

@router.post("/tests/{test_id}/start", response_model=StartAttemptResponse)
def start_exam_attempt(test_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id, Test.user_id == current_user.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test configuration not found")

    # Check for an active in-progress attempt within valid time
    now = datetime.datetime.utcnow()
    active_attempt = db.query(TestAttempt).filter(
        TestAttempt.test_id == test.id,
        TestAttempt.user_id == current_user.id,
        TestAttempt.is_submitted == False,
        TestAttempt.server_deadline > now
    ).order_by(TestAttempt.started_at.desc()).first()

    if not active_attempt:
        # Create new attempt
        deadline = now + datetime.timedelta(minutes=test.time_limit_minutes)
        active_attempt = TestAttempt(
            test_id=test.id,
            user_id=current_user.id,
            started_at=now,
            server_deadline=deadline,
            is_submitted=False,
            status="in_progress",
            max_possible_score=sum(q.marks for q in test.questions)
        )
        db.add(active_attempt)
        db.commit()
        db.refresh(active_attempt)

    # Gather questions & options (answers masked)
    questions_out = []
    saved_answers = {}
    marked_review = []

    # Map existing responses if resuming
    for r in active_attempt.responses:
        if r.selected_option_key:
            saved_answers[str(r.question_id)] = r.selected_option_key
        if r.is_marked_for_review:
            marked_review.append(r.question_id)

    for q in test.questions:
        opts = [OptionOut(id=o.id, option_key=o.option_key, option_text=o.option_text) for o in q.options]
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
            options=opts
        ))

    return StartAttemptResponse(
        attempt_id=active_attempt.id,
        test_id=test.id,
        title=test.title,
        time_limit_minutes=test.time_limit_minutes,
        server_deadline=active_attempt.server_deadline,
        started_at=active_attempt.started_at,
        total_questions=len(questions_out),
        negative_marking=test.negative_marking,
        negative_mark_value=test.negative_mark_value,
        questions=questions_out,
        saved_answers=saved_answers,
        marked_for_review=marked_review
    )

@router.put("/attempts/{attempt_id}/answers/{question_id}", response_model=AnswerSaveResponse)
def autosave_answer(
    attempt_id: int,
    question_id: int,
    req: AnswerSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.is_submitted:
        raise HTTPException(status_code=400, detail="Exam has already been submitted")

    # Check server deadline + grace period
    now = datetime.datetime.utcnow()
    if now > (attempt.server_deadline + datetime.timedelta(seconds=15)):
        # Automatically mark time expired and evaluate
        evaluate_and_grade_attempt(db, attempt)
        raise HTTPException(status_code=400, detail="Examination time limit has expired")

    resp = db.query(StudentResponse).filter(
        StudentResponse.attempt_id == attempt.id,
        StudentResponse.question_id == question_id
    ).first()

    if not resp:
        resp = StudentResponse(attempt_id=attempt.id, question_id=question_id)
        db.add(resp)

    if req.selected_option_key is not None:
        resp.selected_option_key = req.selected_option_key
    if req.is_marked_for_review is not None:
        resp.is_marked_for_review = req.is_marked_for_review
    if req.time_spent_seconds:
        resp.time_spent_seconds += req.time_spent_seconds

    db.commit()
    return AnswerSaveResponse(
        success=True,
        question_id=question_id,
        selected_option_key=resp.selected_option_key,
        is_marked_for_review=resp.is_marked_for_review
    )

@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResultResponse)
def submit_exam_attempt(
    attempt_id: int,
    req: SubmitAttemptRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    client_ans = req.answers if req else None

    # Deterministic scoring & grading
    graded_attempt = evaluate_and_grade_attempt(db, attempt, client_answers=client_ans)

    # Generate 7-step AI feedback for mistakes
    weak_topics = set()
    for resp in graded_attempt.responses:
        q = resp.question
        if not q:
            continue
        if resp.is_correct is False:
            weak_topics.add(q.topic_tag)
            
            corr_opt_key = ""
            corr_opt_text = ""
            sel_opt_text = ""
            for opt in q.options:
                if opt.is_correct:
                    corr_opt_key = opt.option_key
                    corr_opt_text = opt.option_text
                if resp.selected_option_key and opt.option_key == resp.selected_option_key:
                    sel_opt_text = opt.option_text

            # Generate 7-step feedback
            fb = generate_detailed_mistake_feedback(
                question_text=q.question_text,
                selected_option_key=resp.selected_option_key,
                selected_option_text=sel_opt_text,
                correct_option_key=corr_opt_key,
                correct_option_text=corr_opt_text,
                explanation_text=q.explanation_text,
                topic_tag=q.topic_tag,
                source_heading=q.topic_tag,
                source_page=q.source_page
            )
            resp.ai_feedback_json = json.dumps(fb)

    # Executive qualitative summary & study plan
    exec_feedback = generate_attempt_summary_and_plan(
        percentage=graded_attempt.percentage,
        grade=graded_attempt.grade,
        correct_count=graded_attempt.correct_count,
        total_count=len(graded_attempt.test.questions),
        weak_topics=list(weak_topics)
    )
    graded_attempt.ai_summary_feedback = exec_feedback["summary"]
    graded_attempt.ai_study_plan_recommendation = exec_feedback["study_plan"]
    db.commit()

    # Update Topic Mastery & Mistake Notebook
    update_topic_mastery_from_attempt(db, graded_attempt)

    # Build response
    return build_attempt_result_response(db, graded_attempt)

@router.get("/attempts/{attempt_id}/results", response_model=AttemptResultResponse)
def get_attempt_results(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if not attempt.is_submitted:
        # Evaluate if time passed or force submit
        attempt = evaluate_and_grade_attempt(db, attempt)

    return build_attempt_result_response(db, attempt)

@router.get("/attempts", response_model=List[Dict[str, Any]])
def list_student_attempts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    attempts = db.query(TestAttempt).filter(
        TestAttempt.user_id == current_user.id,
        TestAttempt.is_submitted == True
    ).order_by(TestAttempt.submitted_at.desc()).all()

    return [
        {
            "id": a.id,
            "test_id": a.test_id,
            "test_title": a.test.title if a.test else "Exam",
            "score": a.total_score,
            "max_score": a.max_possible_score,
            "percentage": a.percentage,
            "grade": a.grade,
            "time_taken_seconds": a.time_taken_seconds,
            "correct_count": a.correct_count,
            "incorrect_count": a.incorrect_count,
            "unanswered_count": a.unanswered_count,
            "status": a.status,
            "submitted_at": a.submitted_at
        }
        for a in attempts
    ]

def build_attempt_result_response(db: Session, attempt: TestAttempt) -> AttemptResultResponse:
    test = attempt.test
    questions = test.questions

    # Topic breakdown
    topic_stats: Dict[str, Dict[str, int]] = {}
    diff_stats: Dict[str, Dict[str, int]] = {}

    question_results = []
    responses_map = {r.question_id: r for r in attempt.responses}

    for q in questions:
        resp = responses_map.get(q.id)
        user_ans = resp.selected_option_key if resp else None
        is_corr = resp.is_correct if resp else False
        is_unans = (user_ans is None or user_ans == "")
        marks_awd = resp.score_awarded if resp else 0.0

        # Find correct answer description
        corr_ans_str = ""
        for opt in q.options:
            if opt.is_correct:
                corr_ans_str = f"({opt.option_key}) {opt.option_text}"
                break

        # Topic aggregation
        t_tag = q.topic_tag or "General"
        if t_tag not in topic_stats:
            topic_stats[t_tag] = {"total": 0, "correct": 0}
        topic_stats[t_tag]["total"] += 1
        if is_corr:
            topic_stats[t_tag]["correct"] += 1

        # Difficulty aggregation
        d_tag = q.difficulty or "medium"
        if d_tag not in diff_stats:
            diff_stats[d_tag] = {"total": 0, "correct": 0}
        diff_stats[d_tag]["total"] += 1
        if is_corr:
            diff_stats[d_tag]["correct"] += 1

        # AI feedback parsed
        fb_dict = None
        if resp and resp.ai_feedback_json:
            try:
                fb_dict = json.loads(resp.ai_feedback_json)
            except Exception:
                fb_dict = None

        question_results.append(QuestionResultDetail(
            question_id=q.id,
            order_index=q.order_index,
            question_text=q.question_text,
            difficulty=q.difficulty,
            topic_tag=q.topic_tag,
            marks_possible=q.marks,
            marks_awarded=marks_awd,
            user_answer=user_ans,
            correct_answer=corr_ans_str,
            is_correct=is_corr,
            is_unanswered=is_unans,
            explanation=q.explanation_text,
            source_citation={
                "document_id": q.source_document_id,
                "document_title": q.source_document_title,
                "page_number": q.source_page,
                "snippet": q.source_passage_snippet
            },
            ai_feedback=fb_dict
        ))

    # Build topic list
    topic_breakdown = [
        {
            "topic": k,
            "accuracy": round((v["correct"] / v["total"]) * 100.0, 1),
            "correct": v["correct"],
            "total": v["total"]
        }
        for k, v in topic_stats.items()
    ]

    # Build difficulty list
    difficulty_breakdown = [
        {
            "difficulty": k,
            "accuracy": round((v["correct"] / v["total"]) * 100.0, 1),
            "correct": v["correct"],
            "total": v["total"]
        }
        for k, v in diff_stats.items()
    ]

    # Comparison with previous attempt
    prev_attempt = db.query(TestAttempt).filter(
        TestAttempt.test_id == test.id,
        TestAttempt.user_id == attempt.user_id,
        TestAttempt.id != attempt.id,
        TestAttempt.is_submitted == True
    ).order_by(TestAttempt.submitted_at.desc()).first()

    if prev_attempt:
        delta = round(attempt.percentage - prev_attempt.percentage, 1)
        comparison = {
            "has_previous": True,
            "previous_percentage": prev_attempt.percentage,
            "previous_grade": prev_attempt.grade,
            "improvement_percentage": delta,
            "message": f"Improved by +{delta}%!" if delta > 0 else (f"Down by {delta}%" if delta < 0 else "Maintained consistent score.")
        }
    else:
        comparison = {
            "has_previous": False,
            "previous_percentage": None,
            "previous_grade": None,
            "improvement_percentage": 0.0,
            "message": "First recorded attempt on this assessment blueprint."
        }

    return AttemptResultResponse(
        attempt_id=attempt.id,
        test_id=test.id,
        test_title=test.title,
        total_score=attempt.total_score,
        max_possible_score=attempt.max_possible_score,
        percentage=attempt.percentage,
        grade=attempt.grade,
        status=attempt.status,
        time_taken_seconds=attempt.time_taken_seconds,
        correct_count=attempt.correct_count,
        incorrect_count=attempt.incorrect_count,
        unanswered_count=attempt.unanswered_count,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        topic_breakdown=topic_breakdown,
        difficulty_breakdown=difficulty_breakdown,
        comparison_with_previous=comparison,
        ai_summary_feedback=attempt.ai_summary_feedback,
        ai_study_plan_recommendation=attempt.ai_study_plan_recommendation,
        question_results=question_results
    )
