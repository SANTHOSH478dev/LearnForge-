import os
import uuid
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.document import Document, DocumentChunk, ProcessingJob
from app.models.revision import Flashcard
from app.schemas.document import DocumentOut, DocumentDetailOut, DocumentSummaryOut
from app.services.document_service import extract_document, chunk_pages_data, analyze_document_content
from app.dependencies import get_current_user

router = APIRouter(prefix="/documents", tags=["Smart Document Studio"])

@router.post("/upload", response_model=DocumentDetailOut)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 2. Read contents and validate size
    contents = await file.read()
    file_size = len(contents)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )

    # 3. Save to disk securely
    safe_filename = f"{uuid.uuid4().hex}_{os.path.basename(file.filename)}"
    storage_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    with open(storage_path, "wb") as f:
        f.write(contents)

    doc_title = title.strip() if title and title.strip() else os.path.splitext(file.filename)[0]

    # 4. Create Document record
    new_doc = Document(
        user_id=current_user.id,
        title=doc_title,
        file_name=file.filename,
        file_type=file_ext.replace(".", ""),
        file_size_bytes=file_size,
        storage_path=storage_path,
        processing_status="processing"
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # 5. Extract text and chunk
    try:
        pages_data = extract_document(storage_path, new_doc.file_type)
        page_count = len(pages_data) if pages_data else 1
        new_doc.page_count = page_count

        chunks_data = chunk_pages_data(pages_data)
        
        # Save chunks
        for c in chunks_data:
            chunk_rec = DocumentChunk(
                document_id=new_doc.id,
                chunk_index=c["chunk_index"],
                page_number=c["page_number"],
                section_heading=c["section_heading"],
                content=c["content"],
                token_count=c["token_count"]
            )
            db.add(chunk_rec)

        # Content analysis
        analysis = analyze_document_content(chunks_data, doc_title)
        new_doc.summary_text = analysis["summary"]
        new_doc.detected_topics = json.dumps(analysis["topics"])
        new_doc.key_concepts = json.dumps(analysis["key_concepts"])
        new_doc.suggested_questions = json.dumps(analysis["suggested_questions"])
        new_doc.processing_status = "completed"

        # Auto-create initial flashcards from key concepts
        for kc in analysis["key_concepts"][:4]:
            fc = Flashcard(
                user_id=current_user.id,
                document_id=new_doc.id,
                topic=analysis["topics"][0] if analysis["topics"] else "General",
                front_prompt=f"Define or explain the core significance of: {kc.get('term')}",
                back_explanation=kc.get("definition", ""),
                difficulty="medium"
            )
            db.add(fc)

        db.commit()
        db.refresh(new_doc)

    except Exception as e:
        db.rollback()
        new_doc.processing_status = "failed"
        new_doc.error_message = str(e)
        db.commit()
        db.refresh(new_doc)

    return new_doc

@router.get("", response_model=List[DocumentOut])
def get_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.created_at.desc()).all()
    return docs

@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document_detail(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found or unauthorized access")
    return doc

@router.get("/{document_id}/summary", response_model=DocumentSummaryOut)
def get_document_summary(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        key_concepts = json.loads(doc.key_concepts) if doc.key_concepts else []
    except Exception:
        key_concepts = []

    try:
        detected_topics = json.loads(doc.detected_topics) if doc.detected_topics else []
    except Exception:
        detected_topics = []

    try:
        suggested_q = json.loads(doc.suggested_questions) if doc.suggested_questions else []
    except Exception:
        suggested_q = []

    return DocumentSummaryOut(
        id=doc.id,
        title=doc.title,
        page_count=doc.page_count,
        summary_text=doc.summary_text or "No summary available.",
        key_concepts=key_concepts,
        detected_topics=detected_topics,
        suggested_questions=suggested_q
    )

@router.delete("/{document_id}")
def delete_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove file from disk if present
    if doc.storage_path and os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except Exception:
            pass

    db.delete(doc)
    db.commit()
    return {"message": "Document successfully deleted"}

@router.post("/{document_id}/retry")
def retry_document_processing(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.processing_status = "processing"
    doc.error_message = None
    db.commit()

    try:
        pages_data = extract_document(doc.storage_path, doc.file_type)
        doc.page_count = len(pages_data) if pages_data else 1
        chunks_data = chunk_pages_data(pages_data)

        # Delete old chunks
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()

        for c in chunks_data:
            chunk_rec = DocumentChunk(
                document_id=doc.id,
                chunk_index=c["chunk_index"],
                page_number=c["page_number"],
                section_heading=c["section_heading"],
                content=c["content"],
                token_count=c["token_count"]
            )
            db.add(chunk_rec)

        analysis = analyze_document_content(chunks_data, doc.title)
        doc.summary_text = analysis["summary"]
        doc.detected_topics = json.dumps(analysis["topics"])
        doc.key_concepts = json.dumps(analysis["key_concepts"])
        doc.suggested_questions = json.dumps(analysis["suggested_questions"])
        doc.processing_status = "completed"
        db.commit()
    except Exception as e:
        doc.processing_status = "failed"
        doc.error_message = str(e)
        db.commit()

    return {"message": "Processing retried", "status": doc.processing_status}
