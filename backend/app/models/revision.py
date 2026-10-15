import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base

class TopicMastery(Base):
    __tablename__ = "topic_masteries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(100), default="General")
    topic = Column(String(100), nullable=False, index=True)
    total_attempted = Column(Integer, default=0)
    total_correct = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)  # Percentage 0 - 100
    mastery_level = Column(String(50), default="learning")  # learning (<60%), competent (60-80%), mastered (>80%)
    last_attempted_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="topic_masteries")

class MistakeNotebook(Base):
    __tablename__ = "mistake_notebook"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="SET NULL"), nullable=True)
    question_text = Column(Text, nullable=False)
    user_wrong_answer = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    core_concept = Column(String(255), nullable=True)
    topic_tag = Column(String(100), default="General")
    source_reference = Column(String(255), nullable=True)
    reviewed_count = Column(Integer, default=0)
    is_resolved = Column(Boolean, default=False)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="mistakes")

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    topic = Column(String(100), default="General")
    front_prompt = Column(Text, nullable=False)
    back_explanation = Column(Text, nullable=False)
    key_terms = Column(Text, default="[]")  # JSON string
    difficulty = Column(String(50), default="medium")
    interval_days = Column(Integer, default=1)
    repetition_count = Column(Integer, default=0)
    ease_factor = Column(Float, default=2.5)  # SuperMemo SM-2 ease factor
    next_review_date = Column(Date, default=datetime.date.today)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="flashcards")
    document = relationship("Document", back_populates="flashcards")
