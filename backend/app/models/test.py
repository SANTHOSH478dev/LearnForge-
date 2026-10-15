import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_ids = Column(Text, default="[]")  # JSON list of document IDs used as source
    title = Column(String(255), nullable=False)
    subject = Column(String(100), default="General")
    topic = Column(String(100), default="Comprehensive")
    test_type = Column(String(50), default="timed_exam")  # practice, timed_exam, revision, challenge
    difficulty = Column(String(50), default="medium")     # easy, medium, hard, mixed
    total_questions = Column(Integer, default=10)
    time_limit_minutes = Column(Integer, default=15)
    negative_marking = Column(Boolean, default=False)
    negative_mark_value = Column(Float, default=0.25)
    passing_percentage = Column(Float, default=60.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="tests")
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan", order_by="Question.order_index")
    attempts = relationship("TestAttempt", back_populates="test", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False, default=0)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="mcq")  # mcq, true_false, fill_blank, short_answer
    difficulty = Column(String(50), default="medium")
    topic_tag = Column(String(100), default="General")
    marks = Column(Float, default=1.0)
    source_document_id = Column(Integer, nullable=True)
    source_document_title = Column(String(255), nullable=True)
    source_page = Column(Integer, nullable=True)
    source_passage_snippet = Column(Text, nullable=True)
    explanation_text = Column(Text, nullable=False)
    rubric_criteria = Column(Text, nullable=True)  # JSON grading rubric for short_answer

    test = relationship("Test", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.option_key")
    responses = relationship("StudentResponse", back_populates="question", cascade="all, delete-orphan")

class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    option_key = Column(String(10), nullable=False)  # A, B, C, D
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship("Question", back_populates="options")
