import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User, StudentProfile
from app.models.document import Document
from app.models.test import Test
from app.models.attempt import TestAttempt
from app.models.revision import TopicMastery
from app.schemas.profile import DashboardMetrics
from app.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardMetrics)
def get_dashboard_metrics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user.id

    # 1. Document metrics
    total_docs = db.query(Document).filter(Document.user_id == user_id).count()

    # 2. Test attempts
    attempts = db.query(TestAttempt).filter(
        TestAttempt.user_id == user_id,
        TestAttempt.is_submitted == True
    ).order_by(TestAttempt.submitted_at.desc()).all()

    total_tests = len(attempts)
    avg_score = round(sum(a.percentage for a in attempts) / total_tests, 1) if total_tests > 0 else 0.0
    study_seconds = sum(a.time_taken_seconds for a in attempts)
    study_minutes = round(study_seconds / 60)

    # 3. Profile & streak
    profile = current_user.profile
    current_streak = profile.current_streak if profile else 1
    longest_streak = profile.longest_streak if profile else 1
    daily_goal_mins = profile.daily_goal_minutes if profile else 45
    
    # Calculate daily goal progress (today's study minutes)
    today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_study_seconds = sum(
        a.time_taken_seconds for a in attempts if a.submitted_at and a.submitted_at >= today_start
    )
    today_mins = round(today_study_seconds / 60)
    progress_percent = min(100.0, round((today_mins / max(1, daily_goal_mins)) * 100.0, 1))

    # 4. Weekly performance
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly_perf = []
    # Build past 7 days
    today = datetime.date.today()
    for i in range(6, -1, -1):
        day_date = today - datetime.timedelta(days=i)
        day_name = day_date.strftime("%a")
        day_attempts = [
            a for a in attempts if a.submitted_at and a.submitted_at.date() == day_date
        ]
        avg_day_score = round(sum(a.percentage for a in day_attempts) / len(day_attempts), 1) if day_attempts else 0
        weekly_perf.append({
            "day": day_name,
            "date": day_date.strftime("%b %d"),
            "tests_taken": len(day_attempts),
            "score": avg_day_score
        })

    # 5. Subject accuracy
    topic_masteries = db.query(TopicMastery).filter(TopicMastery.user_id == user_id).all()
    subject_map = {}
    for tm in topic_masteries:
        subj = tm.subject or "Core Materials"
        if subj not in subject_map:
            subject_map[subj] = {"correct": 0, "attempted": 0}
        subject_map[subj]["correct"] += tm.total_correct
        subject_map[subj]["attempted"] += tm.total_attempted

    subject_accuracy = []
    for subj, vals in subject_map.items():
        rate = round((vals["correct"] / vals["attempted"]) * 100.0, 1) if vals["attempted"] > 0 else 0.0
        subject_accuracy.append({
            "subject": subj,
            "accuracy": rate,
            "total_questions": vals["attempted"]
        })

    if not subject_accuracy:
        subject_accuracy = [
            {"subject": "Core Concepts", "accuracy": 78.5, "total_questions": 15},
            {"subject": "Applications", "accuracy": 64.0, "total_questions": 12}
        ]

    # 6. Weakest concepts
    weak_records = db.query(TopicMastery).filter(
        TopicMastery.user_id == user_id,
        TopicMastery.accuracy_rate < 70.0
    ).order_by(TopicMastery.accuracy_rate.asc()).limit(4).all()

    weakest_concepts = []
    for wr in weak_records:
        weakest_concepts.append({
            "topic": wr.topic,
            "accuracy": wr.accuracy_rate,
            "attempts": wr.total_attempted
        })

    if not weakest_concepts and total_tests > 0:
        # Pick the lowest accuracy topic available
        lowest = db.query(TopicMastery).filter(TopicMastery.user_id == user_id).order_by(TopicMastery.accuracy_rate.asc()).first()
        if lowest:
            weakest_concepts.append({
                "topic": lowest.topic,
                "accuracy": lowest.accuracy_rate,
                "attempts": lowest.total_attempted
            })

    # 7. Recent attempts
    recent_attempts_list = []
    for a in attempts[:5]:
        recent_attempts_list.append({
            "id": a.id,
            "test_id": a.test_id,
            "title": a.test.title if a.test else "Examination",
            "score": a.total_score,
            "max_score": a.max_possible_score,
            "percentage": a.percentage,
            "grade": a.grade,
            "date": a.submitted_at.strftime("%b %d, %H:%M") if a.submitted_at else "In Progress"
        })

    # 8. Continue learning cards
    latest_docs = db.query(Document).filter(
        Document.user_id == user_id,
        Document.processing_status == "completed"
    ).order_by(Document.created_at.desc()).limit(3).all()

    continue_learning = []
    for d in latest_docs:
        continue_learning.append({
            "document_id": d.id,
            "title": d.title,
            "page_count": d.page_count,
            "topics_count": len(d.detected_topics.split(",")) if d.detected_topics else 3,
            "status": "Ready for Assessment"
        })

    # 9. Recommended Next Step
    if not latest_docs:
        next_step = {
            "title": "Upload Your First Study Material",
            "description": "Upload a PDF, slide deck, or lecture notes to automatically generate your first diagnostic test.",
            "action_text": "Upload Material",
            "action_route": "/documents"
        }
    elif total_tests == 0:
        next_step = {
            "title": f"Take Diagnostic Exam on '{latest_docs[0].title}'",
            "description": "Establish your baseline knowledge with a calibrated 10-question practice test.",
            "action_text": "Start Diagnostic",
            "action_route": f"/tests/create?docId={latest_docs[0].id}"
        }
    elif weakest_concepts:
        next_step = {
            "title": f"Reinforce Weakness: {weakest_concepts[0]['topic']}",
            "description": f"Accuracy is at {weakest_concepts[0]['accuracy']}%. Complete a 5-question targeted adaptive test to boost mastery.",
            "action_text": "Forge Weakness",
            "action_route": "/revision"
        }
    else:
        next_step = {
            "title": "Timed Exam Challenge",
            "description": "Maintain your streak and push your score toward an S-Grade certification standard.",
            "action_text": "Create New Exam",
            "action_route": "/tests/create"
        }

    # 10. Daily Challenge
    daily_challenge = {
        "title": "Daily Precision Sprint",
        "objective": "Score at least 80% on any 10-question timed exam today.",
        "reward_points": "+50 Mastery XP",
        "is_completed": any(a.percentage >= 80.0 and a.submitted_at and a.submitted_at >= today_start for a in attempts)
    }

    return DashboardMetrics(
        total_materials_uploaded=total_docs,
        total_tests_completed=total_tests,
        average_score_percentage=avg_score,
        study_time_minutes=study_minutes,
        current_streak_days=current_streak,
        longest_streak_days=longest_streak,
        daily_goal_minutes=daily_goal_mins,
        daily_goal_progress_percent=progress_percent,
        weekly_performance=weekly_perf,
        subject_accuracy=subject_accuracy,
        weakest_concepts=weakest_concepts,
        recent_attempts=recent_attempts_list,
        continue_learning=continue_learning,
        recommended_next_step=next_step,
        daily_challenge=daily_challenge
    )
