import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.resume import ResumeVersion, Export
from backend.app.services.export_service import export_service

router = APIRouter(prefix="/export", tags=["Document Export"])

@router.get("/{version_id}/pdf")
def export_pdf(version_id: str, db: Session = Depends(get_db)):
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found.")

    sanitized_title = "".join(c for c in version.title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"{sanitized_title}_{version_id[:6]}.pdf"

    try:
        pdf_path = export_service.export_to_pdf(version.tailored_content, output_filename=filename)
        file_size = os.path.getsize(pdf_path)

        # Record export
        exp = Export(
            resume_version_id=version.id,
            format="pdf",
            file_path=pdf_path,
            file_size_bytes=file_size
        )
        db.add(exp)
        db.commit()

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.get("/{version_id}/docx")
def export_docx(version_id: str, db: Session = Depends(get_db)):
    version = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found.")

    sanitized_title = "".join(c for c in version.title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    filename = f"{sanitized_title}_{version_id[:6]}.docx"

    try:
        docx_path = export_service.export_to_docx(version.tailored_content, output_filename=filename)
        file_size = os.path.getsize(docx_path)

        # Record export
        exp = Export(
            resume_version_id=version.id,
            format="docx",
            file_path=docx_path,
            file_size_bytes=file_size
        )
        db.add(exp)
        db.commit()

        return FileResponse(
            path=docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate DOCX: {str(e)}")
