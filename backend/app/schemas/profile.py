from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import datetime

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    academic_level: Optional[str] = None
    primary_subjects: Optional[str] = None  # JSON string
    learning_goals: Optional[str] = None
    daily_goal_minutes: Optional[int] = None
    avatar_url: Optional[str] = None

class StudentProfileOut(BaseModel):
    id: int
    user_id: int
    academic_level: str
    primary_subjects: str
    learning_goals: str
    daily_goal_minutes: int
    current_streak: int
    longest_streak: int
    last_active_date: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class AchievementOut(BaseModel):
    id: int
    badge_type: str
    badge_title: str
    badge_description: str
    icon_name: str
    awarded_at: datetime.datetime

    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    total_materials_uploaded: int
    total_tests_completed: int
    average_score_percentage: float
    study_time_minutes: int
    current_streak_days: int
    longest_streak_days: int
    daily_goal_minutes: int
    daily_goal_progress_percent: float
    weekly_performance: List[Dict[str, Any]]
    subject_accuracy: List[Dict[str, Any]]
    weakest_concepts: List[Dict[str, Any]]
    recent_attempts: List[Dict[str, Any]]
    continue_learning: List[Dict[str, Any]]
    recommended_next_step: Dict[str, Any]
    daily_challenge: Dict[str, Any]
