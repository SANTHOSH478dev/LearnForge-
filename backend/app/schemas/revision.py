from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import datetime

class TopicMasteryOut(BaseModel):
    id: int
    subject: str
    topic: str
    total_attempted: int
    total_correct: int
    accuracy_rate: float
    mastery_level: str
    last_attempted_at: datetime.datetime

    class Config:
        from_attributes = True

class WeaknessConcept(BaseModel):
    topic: str
    subject: str
    accuracy_rate: float
    total_attempted: int
    recommended_focus: str
    suggested_revision_action: str

class WeaknessAnalysisResponse(BaseModel):
    overall_mastery_score: float
    weakest_topics: List[WeaknessConcept]
    moderate_topics: List[WeaknessConcept]
    strong_topics: List[WeaknessConcept]
    recommended_study_hours: float
    suggested_adaptive_test_id: Optional[int] = None

class MistakeItemOut(BaseModel):
    id: int
    question_id: Optional[int]
    attempt_id: Optional[int]
    question_text: str
    user_wrong_answer: Optional[str]
    correct_answer: str
    explanation: str
    core_concept: Optional[str]
    topic_tag: str
    source_reference: Optional[str]
    reviewed_count: int
    is_resolved: bool
    added_at: datetime.datetime

    class Config:
        from_attributes = True

class ResolveMistakeRequest(BaseModel):
    is_resolved: bool

class FlashcardOut(BaseModel):
    id: int
    document_id: Optional[int]
    topic: str
    front_prompt: str
    back_explanation: str
    key_terms: str
    difficulty: str
    interval_days: int
    repetition_count: int
    ease_factor: float
    next_review_date: datetime.date

    class Config:
        from_attributes = True

class FlashcardCreateRequest(BaseModel):
    document_id: Optional[int] = None
    topic: str
    front_prompt: str
    back_explanation: str
    difficulty: Optional[str] = "medium"

class FlashcardReviewRequest(BaseModel):
    rating: int  # 1 (Again/Hard), 2 (Good), 3 (Easy)

class DailyPlanOut(BaseModel):
    today_date: str
    greeting: str
    target_study_minutes: int
    streak_count: int
    due_flashcards_count: int
    unresolved_mistakes_count: int
    primary_revision_topic: str
    recommended_actions: List[Dict[str, Any]]
