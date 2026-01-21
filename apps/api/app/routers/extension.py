from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from app.database import get_db
from app.models.job_posting import JobPosting as JobPostingModel
from app.models.user import User
from app.routers.auth import get_current_user
from typing import Optional as Opt
from app.schemas.job_posting import JobPostingResponse, RawExtraction
from app.schemas.application import ApplicationField
from app.utils.providers import detect_provider
from app.utils.app_logger import app_logger
from datetime import datetime
import json

router = APIRouter()


class ExtensionExtractRequest(BaseModel):
    url: str
    html: Optional[str] = None
    text: Optional[str] = None
    jsonld: Optional[dict] = None
    screenshots: Optional[list] = None


@router.post("/extract", response_model=JobPostingResponse)
async def extension_extract(
    request: ExtensionExtractRequest,
    current_user: Opt[User] = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Accept extraction data from extension"""
    url = request.url
    
    # Try to find existing job posting
    existing_doc = db.job_postings.find_one({"source_url": url})
    existing = JobPostingModel.from_dict(existing_doc) if existing_doc else None
    
    # Build extraction result
    description_html = request.html or ""
    description_text = request.text or ""
    
    # Use JSON-LD if provided
    if request.jsonld:
        job_posting_data = request.jsonld
        if isinstance(job_posting_data, dict) and job_posting_data.get("@type") == "JobPosting":
            description_text = job_posting_data.get("description", description_text)
            title = job_posting_data.get("title")
            company_name = None
            if job_posting_data.get("hiringOrganization"):
                org = job_posting_data["hiringOrganization"]
                company_name = org.get("name") if isinstance(org, dict) else str(org)
        else:
            job_posting_data = request.jsonld
    else:
        job_posting_data = None
        title = None
        company_name = None
    
    # If no text extracted, return error
    if not description_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content extracted from page"
        )
    
    # Detect provider
    provider = detect_provider(url).value
    
    # Create or update job posting
    if existing:
        # Update existing
        db.job_postings.update_one(
            {"source_url": url},
            {"$set": {
                "description_html": description_html or existing.description_html,
                "description_text": description_text or existing.description_text,
                "title": title or existing.title,
                "company_name": company_name or existing.company_name,
                "raw.provider_payload": job_posting_data,
                "raw.extraction_path": "extension_extraction",
                "raw.fetched_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow()
            }}
        )
        # Fetch updated document
        updated_doc = db.job_postings.find_one({"source_url": url})
        job_posting = JobPostingModel.from_dict(updated_doc)
    else:
        # Create new
        raw = {
            "provider_payload": job_posting_data,
            "extraction_path": "extension_extraction",
            "fetched_at": datetime.utcnow().isoformat(),
            "warnings": []
        }
        
        job_posting = JobPostingModel(
            source_url=url,
            provider=provider,
            company_name=company_name,
            title=title,
            description_html=description_html,
            description_text=description_text,
            apply_url=url,  # Default to source URL
            raw=raw
        )
        
        result = db.job_postings.insert_one(job_posting.to_dict())
        job_posting.id = result.inserted_id
    
    # Return response
    return JobPostingResponse(
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
