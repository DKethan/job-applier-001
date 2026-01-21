from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from typing import Optional
from bson import ObjectId
from app.database import get_db
from app.models.job_posting import JobPosting as JobPostingModel
from app.models.profile import Profile as ProfileModel
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.tailor import TailorRequest, TailorResponse
from app.schemas.profile import ProfileSchema
from app.schemas.job_posting import JobPostingResponse, RawExtraction
from app.schemas.application import ApplicationField
from app.services.tailoring import tailoring_service
from app.services.document_generator import document_generator
from app.utils.encryption import encryption_service
from app.utils.app_logger import app_logger
import json
from urllib.parse import urljoin

router = APIRouter()


@router.post("", response_model=TailorResponse)
async def tailor(
    request: TailorRequest,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Tailor resume for a job posting"""
    # Get job posting
    try:
        job_doc = db.job_postings.find_one({"_id": ObjectId(request.job_id)})
    except Exception:
        job_doc = None
    
    if not job_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    
    job_posting = JobPostingModel.from_dict(job_doc)
    
    # Get profile
    try:
        profile_doc = db.profiles.find_one({
            "_id": ObjectId(request.profile_id),
            "user_id": str(current_user.id)
        })
    except Exception:
        profile_doc = None
    
    if not profile_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile_model = ProfileModel.from_dict(profile_doc)
    
    # Decrypt profile
    decrypted_json = encryption_service.decrypt(profile_model.encrypted_json)
    profile = ProfileSchema(**json.loads(decrypted_json))
    
    # Convert job posting to response schema
    job_response = JobPostingResponse(
        id=str(job_posting.id),
        source_url=job_posting.source_url,
        provider=job_posting.provider,
        company_name=job_posting.company_name,
        title=job_posting.title,
        location=job_posting.location,
        employment_type=job_posting.employment_type,
        apply_url=job_posting.apply_url,
        description_html=job_posting.description_html,
        description_text=job_posting.description_text,
        application_form_schema=[ApplicationField(**field) for field in job_posting.application_form_schema] if job_posting.application_form_schema else None,
        raw=RawExtraction(**job_posting.raw),
        created_at=job_posting.created_at,
        updated_at=job_posting.updated_at
    )
    
    # Generate tailoring
    tailoring = await tailoring_service.tailor_resume(job_response, profile)
    
    # Generate documents
    docx_file_id, pdf_file_id = await document_generator.generate_tailored_resume(
        profile, tailoring, request.profile_id
    )
    
    # Build download URLs
    base_url = "http://localhost:8000"  # TODO: Get from settings
    tailoring.tailored_resume_docx_url = urljoin(base_url, f"/v1/downloads/{docx_file_id}")
    tailoring.tailored_resume_pdf_url = urljoin(base_url, f"/v1/downloads/{pdf_file_id}")
    
    return tailoring


@router.get("/{job_id}/{profile_id}/autofill", response_model=dict)
async def get_autofill_data(
    job_id: str,
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Get autofill data for extension"""
    # Verify ownership
    try:
        profile_doc = db.profiles.find_one({
            "_id": ObjectId(profile_id),
            "user_id": str(current_user.id)
        })
    except Exception:
        profile_doc = None
    
    if not profile_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    profile_model = ProfileModel.from_dict(profile_doc)
    
    # Get tailoring result (or generate if not exists)
    # For now, generate on-the-fly
    # In production, you might cache this
    
    try:
        job_doc = db.job_postings.find_one({"_id": ObjectId(job_id)})
    except Exception:
        job_doc = None
    
    if not job_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )
    
    job_posting = JobPostingModel.from_dict(job_doc)
    
    # Decrypt profile
    decrypted_json = encryption_service.decrypt(profile_model.encrypted_json)
    profile = ProfileSchema(**json.loads(decrypted_json))
    
    # Convert job posting
    job_response = JobPostingResponse(
        id=str(job_posting.id),
        source_url=job_posting.source_url,
        provider=job_posting.provider,
        company_name=job_posting.company_name,
        title=job_posting.title,
        location=job_posting.location,
        employment_type=job_posting.employment_type,
        apply_url=job_posting.apply_url,
        description_html=job_posting.description_html,
        description_text=job_posting.description_text,
        application_form_schema=[ApplicationField(**field) for field in job_posting.application_form_schema] if job_posting.application_form_schema else None,
        raw=RawExtraction(**job_posting.raw),
        created_at=job_posting.created_at,
        updated_at=job_posting.updated_at
    )
    
    # Generate tailoring
    tailoring = await tailoring_service.tailor_resume(job_response, profile)
    
    # Return autofill answers
    return {
        "autofill_answers": tailoring.autofill_answers.model_dump()
    }
