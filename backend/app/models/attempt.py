import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base

class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    server_deadline = Column(DateTime, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    is_submitted = Column(Boolean, default=False)
    status = Column(String(50), default="in_progress")  # in_progress, submitted, time_expired
    
    # Scoring & Performance
    total_score = Column(Float, default=0.0)
    max_possible_score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    grade = Column(String(10), default="F")  # S, A, B, C, D, F
    time_taken_seconds = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    unanswered_count = Column(Integer, default=0)
    
    # AI Qualitative Feedback
    ai_summary_feedback = Column(Text, nullable=True)
    ai_study_plan_recommendation = Column(Text, nullable=True)

    test = relationship("Test", back_populates="attempts")
    user = relationship("User", back_populates="attempts")
    responses = relationship("StudentResponse", back_populates="attempt", cascade="all, delete-orphan")

class StudentResponse(Base):
    __tablename__ = "student_responses"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_option_key = Column(String(10), nullable=True)  # A, B, C, D
    text_response = Column(Text, nullable=True)
    is_marked_for_review = Column(Boolean, default=False)
    is_correct = Column(Boolean, nullable=True)
    score_awarded = Column(Float, default=0.0)
    time_spent_seconds = Column(Integer, default=0)
    
    # Detailed 7-step AI Feedback JSON
    ai_feedback_json = Column(Text, nullable=True)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    attempt = relationship("TestAttempt", back_populates="responses")
    question = relationship("Question", back_populates="responses")
