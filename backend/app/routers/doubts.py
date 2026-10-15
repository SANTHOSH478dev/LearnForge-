import re
import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.doubt import DoubtQuery
from app.schemas.doubt import DoubtAskRequest, DoubtResponseOut, DoubtCitation
from app.services.ai_generator import call_gemini_api
from app.dependencies import get_current_user

router = APIRouter(prefix="/doubts", tags=["AI Doubt Solver"])

@router.post("/ask", response_model=DoubtResponseOut)
def ask_doubt(req: DoubtAskRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = current_user.id
    query_text = req.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Find candidate documents
    if req.document_id:
        docs = db.query(Document).filter(
            Document.id == req.document_id,
            Document.user_id == user_id
        ).all()
    else:
        docs = db.query(Document).filter(
            Document.user_id == user_id,
            Document.processing_status == "completed"
        ).all()

    if not docs:
        raise HTTPException(status_code=400, detail="No relevant study materials found to ground the answer.")

    # Retrieve matching chunks
    query_words = set(re.findall(r"\b[A-Za-z]{3,}\b", query_text.lower()))
    candidate_chunks = []

    for doc in docs:
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).all()
        for c in chunks:
            content_lower = c.content.lower()
            match_count = sum(1 for w in query_words if w in content_lower)
            if match_count > 0:
                score = match_count / max(len(query_words), 1)
                candidate_chunks.append({
                    "chunk": c,
                    "doc": doc,
                    "score": round(score, 2)
                })

    # Sort by relevance
    candidate_chunks.sort(key=lambda x: x["score"], reverse=True)
    top_chunks = candidate_chunks[:3]

    citations = []
    citations_data_for_db = []

    if top_chunks:
        for item in top_chunks:
            c = item["chunk"]
            doc = item["doc"]
            cit = DoubtCitation(
                document_id=doc.id,
                document_title=doc.title,
                page_number=c.page_number,
                section_heading=c.section_heading,
                passage_snippet=c.content[:220].strip() + "...",
                relevance_score=item["score"]
            )
            citations.append(cit)
            citations_data_for_db.append(cit.model_dump())

        # Grounding text
        grounding_context = "\n\n".join([
            f"Source: {doc.title} (Page {c.page_number}, Section: {c.section_heading}):\n{c.content[:500]}"
            for item in top_chunks
        ])

        # Ask Gemini if configured
        gemini_prompt = f"""
You are LearnForge AI Doubt Solver. Ground your response strictly in the excerpts below.
Question: {query_text}

GROUNDING PASSAGES:
{grounding_context}

Provide a direct, concise, and helpful answer. Mention the specific page and section cited.
"""
        llm_response = call_gemini_api(gemini_prompt)

        if llm_response:
            answer_text = llm_response.strip()
        else:
            first_c = top_chunks[0]["chunk"]
            first_doc = top_chunks[0]["doc"]
            answer_text = (
                f"Based on your study notes in '{first_doc.title}' (Page {first_c.page_number}, Section: {first_c.section_heading}):\n\n"
                f"{first_c.content[:350]}...\n\n"
                f"Key Takeaway: The material indicates that this concept directly governs the behavior of related operations."
            )
    else:
        answer_text = (
            f"I reviewed your uploaded materials, but could not find a high-confidence match for '{query_text}'. "
            f"Try uploading additional course slides or notes on this topic, or rephrase your question."
        )

    # Save to DoubtQuery history
    record = DoubtQuery(
        user_id=user_id,
        document_id=req.document_id,
        query_text=query_text,
        response_text=answer_text,
        citations_json=json.dumps(citations_data_for_db)
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return DoubtResponseOut(
        id=record.id,
        query_text=record.query_text,
        response_text=record.response_text,
        citations=citations,
        created_at=record.created_at
    )

@router.get("", response_model=List[DoubtResponseOut])
def get_doubt_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(DoubtQuery).filter(
        DoubtQuery.user_id == current_user.id
    ).order_by(DoubtQuery.created_at.desc()).limit(15).all()

    result = []
    for r in records:
        try:
            cit_list = json.loads(r.citations_json) if r.citations_json else []
            citations = [DoubtCitation(**c) for c in cit_list]
        except Exception:
            citations = []
        result.append(DoubtResponseOut(
            id=r.id,
            query_text=r.query_text,
            response_text=r.response_text,
            citations=citations,
            created_at=r.created_at
        ))
    return result
