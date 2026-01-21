from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.application import ApplicationField


class JobIngestRequest(BaseModel):
    url: str


class RawExtraction(BaseModel):
    provider_payload: Optional[Dict[str, Any]] = None
    extraction_path: str
    fetched_at: str  # ISO datetime
    warnings: List[str] = []


class JobPostingResponse(BaseModel):
    id: str
    source_url: str
    provider: str
    company_name: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    apply_url: Optional[str] = None
    description_html: Optional[str] = None
    description_text: str
    application_form_schema: Optional[List[ApplicationField]] = None
    raw: RawExtraction
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobIngestResponse(BaseModel):
    job_posting: JobPostingResponse
    status: str  # "success" | "needs_render" | "needs_extension_extraction"
