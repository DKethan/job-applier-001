import httpx
from typing import Optional
from urllib.parse import urlparse
import re
import logging
from app.ingestion.base import BaseExtractor, ExtractionResult
from app.config import settings
from app.utils.providers import extract_smartrecruiters_ids

logger = logging.getLogger(__name__)


class SmartRecruitersExtractor(BaseExtractor):
    """Extractor for SmartRecruiters job postings"""
    
    def can_extract(self, url: str) -> bool:
        """Check if URL is a SmartRecruiters job posting"""
        try:
            parsed = urlparse(url)
            return bool(re.match(r'.*smartrecruiters\.com.*', parsed.netloc + parsed.path, re.IGNORECASE))
        except Exception:
            return False
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract from SmartRecruiters API (if key available) or fall back to JSON-LD"""
        ids = extract_smartrecruiters_ids(url)
        if not ids:
            return ExtractionResult(
                description_text="",
                extraction_path="smartrecruiters_api",
                warnings=["Could not parse SmartRecruiters URL"]
            )
        
        company_identifier = ids["companyIdentifier"]
        posting_id = ids["postingId"]
        
        # Check if API key is available
        api_key = getattr(settings, 'smartrecruiters_api_key', None)
        
        if api_key:
            return await self._extract_from_api(company_identifier, posting_id, api_key)
        else:
            # Fall back to JSON-LD extraction (done by JSONLDExtractor)
            return ExtractionResult(
                description_text="",
                extraction_path="smartrecruiters_jsonld_fallback",
                warnings=["No API key configured, falling back to JSON-LD extraction"]
            )
    
    async def _extract_from_api(self, company_identifier: str, posting_id: str, api_key: str) -> ExtractionResult:
        """Extract using SmartRecruiters API"""
        api_url = f"https://api.smartrecruiters.com/v1/companies/{company_identifier}/postings/{posting_id}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"X-SmartToken": api_key}
                response = await client.get(api_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                description_html = data.get("jobAd", {}).get("sections", {}).get("jobDescription", {}).get("text", "")
                description_text = self._html_to_text(description_html)
                title = data.get("name")
                company_name = company_identifier
                location = data.get("location", {}).get("city") if data.get("location") else None
                
                # Get apply URL
                apply_url = data.get("applyUrl") or data.get("url")
                
                return ExtractionResult(
                    description_html=description_html,
                    description_text=description_text,
                    title=title,
                    company_name=company_name,
                    location=location,
                    apply_url=apply_url,
                    provider_payload=data,
                    extraction_path="smartrecruiters_api"
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"SmartRecruiters API error: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="smartrecruiters_api",
                warnings=[f"HTTP error: {e.response.status_code}"]
            )
        except Exception as e:
            logger.error(f"Error extracting from SmartRecruiters: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="smartrecruiters_api",
                warnings=[f"Extraction error: {str(e)}"]
            )
    
    def _html_to_text(self, html: str) -> str:
        """Simple HTML to text conversion"""
        if not html:
            return ""
        import re
        text = re.sub(r'<[^>]+>', '', html)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()
