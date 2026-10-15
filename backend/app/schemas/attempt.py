from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import datetime
from app.schemas.test import QuestionOut

class StartAttemptResponse(BaseModel):
    attempt_id: int
    test_id: int
    title: str
    time_limit_minutes: int
    server_deadline: datetime.datetime
    started_at: datetime.datetime
    total_questions: int
    negative_marking: bool
    negative_mark_value: float
    questions: List[QuestionOut]
    saved_answers: Dict[str, str] = {}
    marked_for_review: List[int] = []

class AnswerSaveRequest(BaseModel):
    selected_option_key: Optional[str] = None
    text_response: Optional[str] = None
    is_marked_for_review: Optional[bool] = False
    time_spent_seconds: Optional[int] = 0

class AnswerSaveResponse(BaseModel):
    success: bool
    question_id: int
    selected_option_key: Optional[str] = None
    is_marked_for_review: bool

class SubmitAttemptRequest(BaseModel):
    answers: Optional[Dict[str, str]] = None  # question_id -> option_key mapping

class QuestionResultDetail(BaseModel):
    question_id: int
    order_index: int
    question_text: str
    difficulty: str
    topic_tag: str
    marks_possible: float
    marks_awarded: float
    user_answer: Optional[str] = None
    correct_answer: str
    is_correct: bool
    is_unanswered: bool
    explanation: str
    source_citation: Optional[Dict[str, Any]] = None
    ai_feedback: Optional[Dict[str, Any]] = None  # 7-step feedback breakdown

class AttemptResultResponse(BaseModel):
    attempt_id: int
    test_id: int
    test_title: str
    total_score: float
    max_possible_score: float
    percentage: float
    grade: str
    status: str
    time_taken_seconds: int
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    started_at: datetime.datetime
    submitted_at: Optional[datetime.datetime]
    topic_breakdown: List[Dict[str, Any]]
    difficulty_breakdown: List[Dict[str, Any]]
    comparison_with_previous: Dict[str, Any]
    ai_summary_feedback: Optional[str] = None
    ai_study_plan_recommendation: Optional[str] = None
    question_results: List[QuestionResultDetail]
