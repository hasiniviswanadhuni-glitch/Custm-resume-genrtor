from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExportResponse(BaseModel):
    id: str
    resume_version_id: str
    format: str # pdf, docx
    file_path: str
    file_size_bytes: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}
