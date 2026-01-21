import httpx
from typing import Optional
from urllib.parse import urlparse
import re
import logging
from app.ingestion.base import BaseExtractor, ExtractionResult
from app.utils.providers import extract_ashby_ids

logger = logging.getLogger(__name__)


class AshbyExtractor(BaseExtractor):
    """Extractor for Ashby job postings"""
    
    def can_extract(self, url: str) -> bool:
        """Check if URL is an Ashby job posting"""
        try:
            parsed = urlparse(url)
            return bool(re.match(r'.*ashbyhq\.com.*', parsed.netloc + parsed.path, re.IGNORECASE))
        except Exception:
            return False
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract from Ashby API"""
        ids = extract_ashby_ids(url)
        if not ids:
            return ExtractionResult(
                description_text="",
                extraction_path="ashby_api",
                warnings=["Could not parse Ashby URL"]
            )
        
        company = ids["company"]
        job_id = ids["jobId"]
        
        # Try to find jobs page name (often same as company)
        jobs_page_name = company
        api_url = f"https://api.ashbyhq.com/posting-api/job-board/{jobs_page_name}?includeCompensation=true"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url)
                response.raise_for_status()
                data = response.json()
                
                # Find the specific job in the list
                job_posting = None
                if isinstance(data, dict) and "jobPostings" in data:
                    job_postings = data["jobPostings"]
                    for posting in job_postings:
                        if posting.get("id") == job_id or posting.get("publicJobId") == job_id:
                            job_posting = posting
                            break
                
                if not job_posting:
                    return ExtractionResult(
                        description_text="",
                        extraction_path="ashby_api",
                        warnings=["Job posting not found in API response"]
                    )
                
                description_html = job_posting.get("descriptionHtml", "")
                description_text = job_posting.get("descriptionPlain", "") or self._html_to_text(description_html)
                title = job_posting.get("title")
                company_name = company
                location = job_posting.get("locationName")
                
                # Get apply URL
                apply_url = job_posting.get("publishedAtUrl") or url
                
                return ExtractionResult(
                    description_html=description_html,
                    description_text=description_text,
                    title=title,
                    company_name=company_name,
                    location=location,
                    apply_url=apply_url,
                    provider_payload=job_posting,
                    extraction_path="ashby_api"
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Ashby API error: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="ashby_api",
                warnings=[f"HTTP error: {e.response.status_code}"]
            )
        except Exception as e:
            logger.error(f"Error extracting from Ashby: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="ashby_api",
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
