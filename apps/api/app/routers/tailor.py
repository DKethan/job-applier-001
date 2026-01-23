from fastapi import APIRouter, Depends, HTTPException, status, Request
from pymongo.database import Database
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database import get_db
from app.models.job_posting import JobPosting as JobPostingModel
from app.models.profile import Profile as ProfileModel
from app.models.job_application import JobApplication
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
from datetime import datetime
from urllib.parse import urljoin

router = APIRouter()


@router.get("/templates", response_model=Dict[str, Dict[str, str]])
async def get_available_templates():
    """Get list of available resume templates"""
    from app.services.document_generator import document_generator
    return document_generator.get_available_templates()


@router.post("", response_model=TailorResponse)
async def tailor(
    request: TailorRequest,
    req: Request,
    template_id: str = "modern-professional",
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

    # Get original file information
    original_file_id = profile_model.original_file_id
    original_file_ext = profile_model.original_file_ext

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
    docx_file_id, cover_letter_file_id, package_file_id = await document_generator.generate_tailored_resume(
        profile, tailoring, job_response, template_id, request.profile_id, original_file_id, original_file_ext
    )

    app_logger.log_info(f"Generated files - DOCX: {docx_file_id}, Cover Letter: {cover_letter_file_id}, Package: {package_file_id}")

    # Build download URLs using the request's base URL
    base_url = f"{req.url.scheme}://{req.url.hostname}"
    if req.url.port and req.url.port != (443 if req.url.scheme == 'https' else 80):
        base_url += f":{req.url.port}"

    tailoring.tailored_resume_docx_url = urljoin(base_url, f"/v1/downloads/{docx_file_id}")

    # Add additional download URLs if files were generated
    if cover_letter_file_id:
        tailoring.cover_letter_docx_url = urljoin(base_url, f"/v1/downloads/{cover_letter_file_id}")
        app_logger.log_info(f"Cover letter URL: {tailoring.cover_letter_docx_url}")
    if package_file_id:
        tailoring.application_package_docx_url = urljoin(base_url, f"/v1/downloads/package/{package_file_id}")
        app_logger.log_info(f"Application package URL: {tailoring.application_package_docx_url}")

    # Save job application metadata for tracking
    try:
        job_application_data = {
            "user_id": str(current_user.id),
            "job_id": str(job_posting.id),
            "job_title": job_posting.title or "Untitled Position",
            "company_name": job_posting.company_name or "Unknown Company",
            "job_url": job_posting.source_url,
            "tailoring_summary": {
                "jd_summary": tailoring.jd_summary,
                "skills_required": tailoring.skills_required,
                "bullets_count": len(tailoring.suggested_bullets),
                "has_cover_letter": bool(tailoring.cover_letter_text),
                "tailored_at": datetime.utcnow().isoformat()
            },
            "file_ids": {
                "resume_docx": docx_file_id,
                "cover_letter_docx": cover_letter_file_id,
                "package_zip": package_file_id
            },
            "applied_date": datetime.utcnow(),
            "status": "tailored",
            "notes": f"Tailored resume for {job_posting.title or 'position'} at {job_posting.company_name or 'company'}"
        }

        # Use upsert to either insert new record or update existing one
        db.job_applications.update_one(
            {"user_id": str(current_user.id), "job_id": str(job_posting.id)},
            {"$set": job_application_data},
            upsert=True
        )
        app_logger.log_info(f"Saved job application metadata for user {current_user.id}, job {job_posting.id}")
    except Exception as e:
        app_logger.log_error(f"Failed to save job application metadata: {e}")

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


@router.get("/applications", response_model=List[Dict[str, Any]])
async def get_user_applications(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Get user's job applications for review"""
    try:
        applications = list(db.job_applications.find({"user_id": str(current_user.id)}).sort("applied_date", -1))
        # Convert ObjectId to string for JSON response
        for app in applications:
            app["_id"] = str(app["_id"])
        return applications
    except Exception as e:
        app_logger.log_error(f"Failed to fetch user applications: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch applications")
