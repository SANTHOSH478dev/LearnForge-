import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, pptx, txt
    file_size_bytes = Column(BigInteger, default=0)
    storage_path = Column(String(500), nullable=False)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    page_count = Column(Integer, default=1)
    summary_text = Column(Text, nullable=True)
    detected_topics = Column(Text, default="[]")  # JSON string of detected topics
    key_concepts = Column(Text, default="[]")    # JSON string of terms & definitions
    suggested_questions = Column(Text, default="[]") # JSON string
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan", order_by="DocumentChunk.chunk_index")
    processing_jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    page_number = Column(Integer, default=1)
    section_heading = Column(String(255), default="General Section")
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)

    document = relationship("Document", back_populates="chunks")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="processing")  # processing, completed, failed
    progress = Column(Integer, default=0)              # 0 to 100 percentage
    stage = Column(String(100), default="extracting")  # extracting, chunking, analyzing, completed
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="processing_jobs")
