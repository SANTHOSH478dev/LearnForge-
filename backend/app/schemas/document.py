from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import datetime

class DocumentChunkOut(BaseModel):
    id: int
    chunk_index: int
    page_number: int
    section_heading: str
    content: str
    token_count: int

    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    user_id: int
    title: str
    file_name: str
    file_type: str
    file_size_bytes: int
    processing_status: str
    page_count: int
    detected_topics: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class DocumentDetailOut(BaseModel):
    id: int
    user_id: int
    title: str
    file_name: str
    file_type: str
    file_size_bytes: int
    processing_status: str
    page_count: int
    summary_text: Optional[str] = None
    detected_topics: str
    key_concepts: str
    suggested_questions: str
    error_message: Optional[str] = None
    created_at: datetime.datetime
    chunks: List[DocumentChunkOut] = []

    class Config:
        from_attributes = True

class DocumentSummaryOut(BaseModel):
    id: int
    title: str
    page_count: int
    summary_text: str
    key_concepts: List[Dict[str, str]]
    detected_topics: List[str]
    suggested_questions: List[Dict[str, Any]]
