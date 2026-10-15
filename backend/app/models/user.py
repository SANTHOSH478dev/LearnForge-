import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="student")  # "student", "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="user", cascade="all, delete-orphan")
    attempts = relationship("TestAttempt", back_populates="user", cascade="all, delete-orphan")
    topic_masteries = relationship("TopicMastery", back_populates="user", cascade="all, delete-orphan")
    mistakes = relationship("MistakeNotebook", back_populates="user", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="user", cascade="all, delete-orphan")
    doubts = relationship("DoubtQuery", back_populates="user", cascade="all, delete-orphan")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    academic_level = Column(String(100), default="Undergraduate")
    primary_subjects = Column(Text, default="[]")  # JSON encoded list of strings
    learning_goals = Column(Text, default="Master course material and ace exams")
    daily_goal_minutes = Column(Integer, default=45)
    current_streak = Column(Integer, default=1)
    longest_streak = Column(Integer, default=1)
    last_active_date = Column(String(20), default=lambda: datetime.date.today().isoformat())
    avatar_url = Column(String(500), nullable=True)

    user = relationship("User", back_populates="profile")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_type = Column(String(100), nullable=False)  # "first_upload", "perfect_score", "streak_7", "exam_master", etc.
    badge_title = Column(String(255), nullable=False)
    badge_description = Column(Text, nullable=False)
    icon_name = Column(String(100), default="Award")
    awarded_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="achievements")
