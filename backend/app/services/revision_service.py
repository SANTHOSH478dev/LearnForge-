import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.attempt import TestAttempt, StudentResponse
from app.models.test import Question
from app.models.revision import TopicMastery, MistakeNotebook, Flashcard
from app.models.user import StudentProfile

def update_topic_mastery_from_attempt(db: Session, attempt: TestAttempt):
    """Update topic accuracy statistics after an exam attempt."""
    user_id = attempt.user_id
    
    # Group responses by topic
    for resp in attempt.responses:
        q = resp.question
        if not q:
            continue
        topic_name = q.topic_tag or "General Concepts"
        subject_name = attempt.test.subject or "General"

        mastery = db.query(TopicMastery).filter(
            TopicMastery.user_id == user_id,
            TopicMastery.topic == topic_name
        ).first()

        if not mastery:
            mastery = TopicMastery(
                user_id=user_id,
                subject=subject_name,
                topic=topic_name,
                total_attempted=0,
                total_correct=0,
                accuracy_rate=0.0,
                mastery_level="learning"
            )
            db.add(mastery)

        mastery.total_attempted += 1
        if resp.is_correct:
            mastery.total_correct += 1

        accuracy = (mastery.total_correct / mastery.total_attempted) * 100.0
        mastery.accuracy_rate = round(accuracy, 1)

        if mastery.accuracy_rate >= 80.0 and mastery.total_attempted >= 3:
            mastery.mastery_level = "mastered"
        elif mastery.accuracy_rate >= 60.0:
            mastery.mastery_level = "competent"
        else:
            mastery.mastery_level = "learning"

        mastery.last_attempted_at = datetime.datetime.utcnow()

    # Populate mistake notebook for wrong answers
    for resp in attempt.responses:
        if resp.is_correct is False:
            q = resp.question
            if not q:
                continue

            # Check if mistake already in notebook
            existing = db.query(MistakeNotebook).filter(
                MistakeNotebook.user_id == user_id,
                MistakeNotebook.question_id == q.id
            ).first()

            correct_text = "N/A"
            for opt in q.options:
                if opt.is_correct:
                    correct_text = f"({opt.option_key}) {opt.option_text}"
                    break

            wrong_text = f"Option {resp.selected_option_key}" if resp.selected_option_key else "Left Unanswered"
            ref_str = f"Page {q.source_page}" if q.source_page else "Document Notes"

            if not existing:
                mistake_entry = MistakeNotebook(
                    user_id=user_id,
                    question_id=q.id,
                    attempt_id=attempt.id,
                    question_text=q.question_text,
                    user_wrong_answer=wrong_text,
                    correct_answer=correct_text,
                    explanation=q.explanation_text,
                    core_concept=q.topic_tag,
                    topic_tag=q.topic_tag,
                    source_reference=ref_str,
                    reviewed_count=0,
                    is_resolved=False
                )
                db.add(mistake_entry)

    db.commit()

def calculate_sm2_interval(rating: int, repetitions: int, ease_factor: float, interval_days: int) -> tuple[int, int, float]:
    """
    SuperMemo SM-2 Spaced Repetition calculation:
    rating: 1 (Hard/Again), 2 (Good), 3 (Easy)
    Returns: (new_repetitions, new_interval_days, new_ease_factor)
    """
    # Map rating 1, 2, 3 to standard SM-2 grade 0-5
    # 1 -> grade 2 (fail/hard), 2 -> grade 4 (good), 3 -> grade 5 (easy)
    grade = 2 if rating == 1 else (4 if rating == 2 else 5)

    new_ef = ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    new_ef = max(1.3, round(new_ef, 2))

    if grade < 3:
        new_reps = 0
        new_interval = 1
    else:
        new_reps = repetitions + 1
        if new_reps == 1:
            new_interval = 1
        elif new_reps == 2:
            new_interval = 6
        else:
            new_interval = int(round(interval_days * new_ef))

    return new_reps, new_interval, new_ef
