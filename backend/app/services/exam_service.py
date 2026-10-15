import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.attempt import TestAttempt, StudentResponse
from app.models.test import Test, Question, QuestionOption

def calculate_attempt_grade(percentage: float) -> str:
    """Standardized collegiate grading scale."""
    if percentage >= 90.0:
        return "S"
    elif percentage >= 80.0:
        return "A"
    elif percentage >= 70.0:
        return "B"
    elif percentage >= 60.0:
        return "C"
    elif percentage >= 50.0:
        return "D"
    else:
        return "F"

def evaluate_and_grade_attempt(
    db: Session,
    attempt: TestAttempt,
    client_answers: Dict[str, str] = None
) -> TestAttempt:
    """
    Deterministic server-side grading engine:
    Evaluates responses against official question options, enforces negative marking if enabled,
    and calculates final score, accuracy, and grade.
    """
    if attempt.is_submitted:
        # Idempotent: return already graded attempt
        return attempt

    now = datetime.datetime.utcnow()
    attempt.submitted_at = now
    attempt.is_submitted = True

    # Check deadline
    grace_period = datetime.timedelta(seconds=15)
    if now > (attempt.server_deadline + grace_period):
        attempt.status = "time_expired"
    else:
        attempt.status = "submitted"

    # Calculate time taken
    time_taken = int((now - attempt.started_at).total_seconds())
    max_seconds = attempt.test.time_limit_minutes * 60
    attempt.time_taken_seconds = min(time_taken, max_seconds)

    test = attempt.test
    questions = db.query(Question).filter(Question.test_id == test.id).all()
    
    # Load or initialize responses map
    existing_responses = {str(r.question_id): r for r in attempt.responses}
    
    total_score = 0.0
    max_score = 0.0
    correct_cnt = 0
    incorrect_cnt = 0
    unanswered_cnt = 0

    for q in questions:
        max_score += q.marks
        qid_str = str(q.id)

        # Get response object
        resp = existing_responses.get(qid_str)
        if not resp:
            resp = StudentResponse(attempt_id=attempt.id, question_id=q.id)
            db.add(resp)
            existing_responses[qid_str] = resp

        # Check client answers update if provided
        if client_answers and qid_str in client_answers:
            resp.selected_option_key = client_answers[qid_str]

        # Find correct option
        correct_option = None
        for opt in q.options:
            if opt.is_correct:
                correct_option = opt.option_key
                break

        selected = resp.selected_option_key

        if not selected or selected == "":
            resp.is_correct = False
            resp.score_awarded = 0.0
            unanswered_cnt += 1
        elif selected == correct_option:
            resp.is_correct = True
            resp.score_awarded = q.marks
            correct_cnt += 1
            total_score += q.marks
        else:
            resp.is_correct = False
            if test.negative_marking:
                deduction = test.negative_mark_value or 0.25
                resp.score_awarded = -deduction
                total_score -= deduction
            else:
                resp.score_awarded = 0.0
            incorrect_cnt += 1

    # Bounds check total score
    total_score = max(0.0, total_score)
    max_score = max(1.0, max_score)
    percentage = round((total_score / max_score) * 100.0, 1)

    attempt.total_score = round(total_score, 2)
    attempt.max_possible_score = round(max_score, 2)
    attempt.percentage = percentage
    attempt.grade = calculate_attempt_grade(percentage)
    attempt.correct_count = correct_cnt
    attempt.incorrect_count = incorrect_cnt
    attempt.unanswered_count = unanswered_cnt

    db.commit()
    db.refresh(attempt)
    return attempt
