from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.attempt import TestAttempt
from app.routers.attempts import build_attempt_result_response
from app.services.pdf_service import generate_exam_report_pdf
from app.dependencies import get_current_user

router = APIRouter(prefix="/export", tags=["Exportable Reports"])

@router.get("/attempts/{attempt_id}/pdf")
def export_attempt_pdf(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")

    result_data = build_attempt_result_response(db, attempt)
    pdf_buffer = generate_exam_report_pdf(
        attempt_data=result_data.model_dump(),
        student_name=current_user.full_name
    )

    filename = f"LearnForge_Assessment_Report_Attempt_{attempt.id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
