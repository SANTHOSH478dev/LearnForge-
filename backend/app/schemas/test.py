from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import datetime

class OptionCreate(BaseModel):
    option_key: str
    option_text: str
    is_correct: bool = False

class OptionOut(BaseModel):
    id: int
    option_key: str
    option_text: str

    class Config:
        from_attributes = True

class OptionOutWithAnswer(OptionOut):
    is_correct: bool

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str = "mcq"  # mcq, true_false, fill_blank, short_answer
    difficulty: str = "medium"
    topic_tag: str = "General"
    marks: float = 1.0
    source_document_id: Optional[int] = None
    source_document_title: Optional[str] = None
    source_page: Optional[int] = None
    source_passage_snippet: Optional[str] = None
    explanation_text: str
    options: List[OptionCreate] = []

class QuestionOut(BaseModel):
    id: int
    order_index: int
    question_text: str
    question_type: str
    difficulty: str
    topic_tag: str
    marks: float
    source_document_id: Optional[int] = None
    source_document_title: Optional[str] = None
    source_page: Optional[int] = None
    source_passage_snippet: Optional[str] = None
    options: List[OptionOut] = []

    class Config:
        from_attributes = True

class QuestionDetailOut(QuestionOut):
    explanation_text: str
    options: List[OptionOutWithAnswer] = []

class GenerateTestRequest(BaseModel):
    document_ids: List[int]
    title: Optional[str] = None
    subject: Optional[str] = "Computer Science"
    topic: Optional[str] = None
    question_count: int = 10
    difficulty: str = "medium"  # easy, medium, hard, mixed
    test_type: str = "timed_exam"  # practice, timed_exam, revision, challenge
    question_types: List[str] = ["mcq"]
    time_limit_minutes: int = 15
    negative_marking: bool = False
    negative_mark_value: float = 0.25

class TestOut(BaseModel):
    id: int
    user_id: int
    title: str
    subject: str
    topic: str
    test_type: str
    difficulty: str
    total_questions: int
    time_limit_minutes: int
    negative_marking: bool
    negative_mark_value: float
    passing_percentage: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TestDetailOut(TestOut):
    questions: List[QuestionOut] = []

class ExamBlueprintRequest(BaseModel):
    document_ids: List[int]
    total_questions: int = 15
    target_difficulty: str = "mixed"

class ExamBlueprintResponse(BaseModel):
    title: str
    summary: str
    topics: List[Dict[str, Any]]
    difficulty_split: Dict[str, int]
    recommended_time_minutes: int
