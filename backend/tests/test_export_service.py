import os
import pytest
from backend.app.services.export_service import export_service

def test_pdf_and_docx_export_generation(tmp_path):
    sample_content = {
        "full_name": "Jordan Smith",
        "email": "jordan@example.com",
        "phone": "+1 555-0199",
        "location": "Boston, MA",
        "professional_summary": "Motivated software engineer with experience in full stack web development.",
        "skills": [
            {"name": "Python"},
            {"name": "TypeScript"},
            {"name": "FastAPI"}
        ],
        "experience": [
            {
                "position": "Junior Engineer",
                "company": "Apex Labs",
                "start_date": "2023",
                "end_date": "Present",
                "bullets": ["Maintained RESTful APIs in Python.", "Increased test coverage."]
            }
        ],
        "projects": [
            {
                "title": "Cloud Dashboard",
                "technologies": ["Python", "React"],
                "bullets": ["Engineered metrics tracking dashboard."]
            }
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "Boston University",
                "start_date": "2019",
                "end_date": "2023"
            }
        ],
        "certifications": []
    }

    # Generate PDF
    pdf_path = export_service.export_to_pdf(sample_content, output_filename="test_out.pdf")
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 500 # Valid non-empty document

    # Generate DOCX
    docx_path = export_service.export_to_docx(sample_content, output_filename="test_out.docx")
    assert os.path.exists(docx_path)
    assert os.path.getsize(docx_path) > 500 # Valid non-empty document

    # Clean up test files
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    if os.path.exists(docx_path):
        os.remove(docx_path)
