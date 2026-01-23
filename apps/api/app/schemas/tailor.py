from pydantic import BaseModel
from typing import Dict, List, Any, Optional


class SuggestedBullet(BaseModel):
    role_id: Optional[str] = None  # Reference to work_experience or project
    original: str
    tailored: str


class Gap(BaseModel):
    skill: Optional[str] = None
    experience: Optional[str] = None
    note: str


class TailorRequest(BaseModel):
    job_id: str
    profile_id: str


class AutofillAnswers(BaseModel):
    # Semantic field name -> value mapping
    legalName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    workAuth: Optional[str] = None
    visaStatus: Optional[str] = None
    salaryExpectation: Optional[str] = None
    availability: Optional[str] = None
    relocation: Optional[str] = None
    remote: Optional[str] = None
    # Allow additional fields
    extra: Dict[str, Any] = {}


class TailorResponse(BaseModel):
    jd_summary: str
    skills_required: List[str]
    gaps: List[Gap]
    suggested_bullets: List[SuggestedBullet]
    cover_letter_text: str
    autofill_answers: AutofillAnswers
    tailored_resume_docx_url: str
    cover_letter_docx_url: Optional[str] = None
    application_package_docx_url: Optional[str] = None
