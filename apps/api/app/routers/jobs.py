from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel
from app.database import get_db
from app.models.job_posting import JobPosting as JobPostingModel
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.job_posting import JobIngestRequest, JobIngestResponse, JobPostingResponse, RawExtraction
from app.schemas.application import ApplicationField
from app.ingestion import (
    GreenhouseExtractor,
    LeverExtractor,
    AshbyExtractor,
    SmartRecruitersExtractor,
    JSONLDExtractor,
    ReadabilityExtractor,
    PlaywrightFallbackExtractor,
)
from app.utils.providers import detect_provider
from app.utils.app_logger import app_logger
from datetime import datetime

router = APIRouter()

# Ordered list of extractors (most specific first)
EXTRACTORS = [
    GreenhouseExtractor(),
    LeverExtractor(),
    AshbyExtractor(),
    SmartRecruitersExtractor(),
    JSONLDExtractor(),
    ReadabilityExtractor(),
]


async def extract_job_posting(url: str) -> tuple[JobPostingModel, str]:
    """Extract job posting using provider-specific extractors"""
    provider = detect_provider(url).value
    
    # Try provider-specific extractors first
    result = None
    extraction_status = "success"
    
    for extractor in EXTRACTORS:
        if extractor.can_extract(url):
            try:
                result = await extractor.extract(url)
                if result.description_text:
                    break
            except Exception as e:
                app_logger.log_warning(f"Extractor {extractor.__class__.__name__} failed: {e}")
                continue
    
    # If no extractor worked, try Playwright fallback
    if not result or not result.description_text:
        playwright_extractor = PlaywrightFallbackExtractor()
        if playwright_extractor.can_extract(url):
            try:
                result = await playwright_extractor.extract(url)
                if not result.description_text:
                    extraction_status = "needs_extension_extraction"
            except Exception as e:
                app_logger.log_error(f"Playwright extraction failed: {e}")
                extraction_status = "needs_extension_extraction"
    
    # If still no content, return error status
    if not result or not result.description_text:
        extraction_status = "needs_extension_extraction"
        # Create minimal result
        from app.ingestion.base import ExtractionResult
        result = ExtractionResult(
            description_text="",
            extraction_path="failed",
            warnings=["Could not extract job posting. Please use extension extraction."]
        )
    
    # Convert to database model
    raw_extraction_dict = result.to_dict()
    
    job_posting = JobPostingModel(
        source_url=url,
        provider=provider,
        company_name=result.company_name,
        title=result.title,
        location=result.location,
        employment_type=result.employment_type,
        apply_url=result.apply_url or url,
        description_html=result.description_html,
        description_text=result.description_text,
        application_form_schema=[field.model_dump() if hasattr(field, 'model_dump') else field for field in result.application_form_schema] if result.application_form_schema else None,
        raw=raw_extraction_dict
    )
    
    return job_posting, extraction_status


@router.post("/ingest", response_model=JobIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_job(
    request: JobIngestRequest,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Ingest job posting from URL"""
    url = request.url
    
    # Check if already exists
    existing_doc = db.job_postings.find_one({"source_url": url})
    if existing_doc:
        existing = JobPostingModel.from_dict(existing_doc)
        job_response = JobPostingResponse(
            id=str(existing.id),
            source_url=existing.source_url,
            provider=existing.provider,
            company_name=existing.company_name,
            title=existing.title,
            location=existing.location,
            employment_type=existing.employment_type,
            apply_url=existing.apply_url,
            description_html=existing.description_html,
            description_text=existing.description_text,
            application_form_schema=[ApplicationField(**field) for field in existing.application_form_schema] if existing.application_form_schema else None,
            raw=RawExtraction(**existing.raw),
            created_at=existing.created_at,
            updated_at=existing.updated_at
        )
        return JobIngestResponse(
            job_posting=job_response,
            status="success"
        )
    
    # Extract job posting
    job_posting, status_str = await extract_job_posting(url)
    
    # Save to database
    try:
        result = db.job_postings.insert_one(job_posting.to_dict())
        job_posting.id = result.inserted_id
    except DuplicateKeyError:
        # If duplicate, find existing
        existing_doc = db.job_postings.find_one({"source_url": url})
        if existing_doc:
            job_posting = JobPostingModel.from_dict(existing_doc)
    
    # Convert to response schema
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
    
    return JobIngestResponse(
        job_posting=job_response,
        status=status_str
    )


@router.get("/{job_id}", response_model=JobPostingResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Get job posting by ID"""
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
    
    # Convert to response schema
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
