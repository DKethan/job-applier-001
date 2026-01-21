from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas.job_posting import RawExtraction
from app.schemas.application import ApplicationField


class ExtractionResult:
    """Result from job posting extraction"""
    def __init__(
        self,
        description_html: Optional[str] = None,
        description_text: str = "",
        title: Optional[str] = None,
        company_name: Optional[str] = None,
        location: Optional[str] = None,
        employment_type: Optional[str] = None,
        apply_url: Optional[str] = None,
        application_form_schema: Optional[List[ApplicationField]] = None,
        provider_payload: Optional[Dict[str, Any]] = None,
        extraction_path: str = "unknown",
        warnings: Optional[List[str]] = None,
    ):
        self.description_html = description_html
        self.description_text = description_text
        self.title = title
        self.company_name = company_name
        self.location = location
        self.employment_type = employment_type
        self.apply_url = apply_url
        self.application_form_schema = application_form_schema or []
        self.provider_payload = provider_payload
        self.extraction_path = extraction_path
        self.warnings = warnings or []

    def to_raw_extraction(self) -> RawExtraction:
        return RawExtraction(
            provider_payload=self.provider_payload,
            extraction_path=self.extraction_path,
            fetched_at=datetime.utcnow().isoformat(),
            warnings=self.warnings
        )
    
    def to_dict(self) -> dict:
        """Convert to dict for storage"""
        return {
            "provider_payload": self.provider_payload,
            "extraction_path": self.extraction_path,
            "fetched_at": datetime.utcnow().isoformat(),
            "warnings": self.warnings
        }


class BaseExtractor(ABC):
    """Base class for job posting extractors"""
    
    @abstractmethod
    def can_extract(self, url: str) -> bool:
        """Check if this extractor can handle the URL"""
        pass
    
    @abstractmethod
    async def extract(self, url: str) -> ExtractionResult:
        """Extract job posting data from URL"""
        pass
