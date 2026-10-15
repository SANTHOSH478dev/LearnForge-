from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.attempt import TestAttempt
from app.models.revision import TopicMastery
from app.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Performance Analytics"])

@router.get("/performance")
def get_performance_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    user_id = current_user.id

    # 1. Historical score progression
    attempts = db.query(TestAttempt).filter(
        TestAttempt.user_id == user_id,
        TestAttempt.is_submitted == True
    ).order_by(TestAttempt.submitted_at.asc()).all()

    score_history = []
    for idx, a in enumerate(attempts, 1):
        score_history.append({
            "attempt_number": idx,
            "test_title": a.test.title if a.test else f"Test #{idx}",
            "percentage": a.percentage,
            "grade": a.grade,
            "date": a.submitted_at.strftime("%b %d") if a.submitted_at else f"Attempt {idx}",
            "time_minutes": round(a.time_taken_seconds / 60, 1)
        })

    # 2. Topic accuracy breakdown
    masteries = db.query(TopicMastery).filter(TopicMastery.user_id == user_id).all()
    topic_accuracy = []
    for m in masteries:
        topic_accuracy.append({
            "topic": m.topic,
            "subject": m.subject,
            "accuracy": m.accuracy_rate,
            "mastery_level": m.mastery_level,
            "total_attempted": m.total_attempted
        })

    # 3. Grade distribution
    grades = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for a in attempts:
        g = a.grade or "F"
        grades[g] = grades.get(g, 0) + 1

    grade_distribution = [{"grade": k, "count": v} for k, v in grades.items()]

    # 4. Total Stats
    total_time_mins = round(sum(a.time_taken_seconds for a in attempts) / 60)
    avg_score = round(sum(a.percentage for a in attempts) / len(attempts), 1) if attempts else 0.0

    return {
        "score_history": score_history,
        "topic_accuracy": topic_accuracy,
        "grade_distribution": grade_distribution,
        "total_assessments_taken": len(attempts),
        "total_study_minutes": total_time_mins,
        "average_score": avg_score
    }
