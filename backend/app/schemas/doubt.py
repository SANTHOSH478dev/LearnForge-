from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import datetime

class DoubtCitation(BaseModel):
    document_id: Optional[int] = None
    document_title: str
    page_number: Optional[int] = None
    section_heading: Optional[str] = None
    passage_snippet: str
    relevance_score: float

class DoubtAskRequest(BaseModel):
    query: str
    document_id: Optional[int] = None  # If None, searches across all student's documents

class DoubtResponseOut(BaseModel):
    id: int
    query_text: str
    response_text: str
    citations: List[DoubtCitation] = []
    created_at: datetime.datetime

    class Config:
        from_attributes = True
