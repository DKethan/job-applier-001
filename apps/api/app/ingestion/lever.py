import httpx
from typing import Optional
from urllib.parse import urlparse
import re
import logging
from app.ingestion.base import BaseExtractor, ExtractionResult
from app.utils.providers import extract_lever_ids

logger = logging.getLogger(__name__)


class LeverExtractor(BaseExtractor):
    """Extractor for Lever job postings"""
    
    def can_extract(self, url: str) -> bool:
        """Check if URL is a Lever job posting"""
        try:
            parsed = urlparse(url)
            return bool(re.match(r'.*lever\.co.*', parsed.netloc + parsed.path, re.IGNORECASE))
        except Exception:
            return False
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract from Lever API"""
        ids = extract_lever_ids(url)
        if not ids:
            return ExtractionResult(
                description_text="",
                extraction_path="lever_api",
                warnings=["Could not parse Lever URL"]
            )
        
        account = ids["account"]
        posting_id = ids["postingId"]
        api_url = f"https://api.lever.co/v0/postings/{account}/{posting_id}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url)
                response.raise_for_status()
                data = response.json()
                
                description_html = data.get("descriptionPlain", "") or data.get("description", "")
                description_text = description_html  # Lever API returns plain text
                title = data.get("text")
                company_name = data.get("hostedUrl", "").split("//")[-1].split(".")[0] if data.get("hostedUrl") else None
                
                # Get apply URL
                apply_url = data.get("hostedUrl") or data.get("applyUrl")
                if not apply_url:
                    apply_url = f"https://jobs.lever.co/{account}/{posting_id}"
                
                # Extract questions
                application_form_schema = []
                if data.get("lists"):
                    for idx, list_item in enumerate(data.get("lists", [])):
                        if list_item.get("text"):
                            # Convert lists to questions if they seem like application questions
                            pass  # Simplified - would need to parse lists structure
                
                return ExtractionResult(
                    description_html=description_html,
                    description_text=description_text,
                    title=title,
                    company_name=company_name,
                    apply_url=apply_url,
                    application_form_schema=application_form_schema,
                    provider_payload=data,
                    extraction_path="lever_api"
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Lever API error: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="lever_api",
                warnings=[f"HTTP error: {e.response.status_code}"]
            )
        except Exception as e:
            logger.error(f"Error extracting from Lever: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="lever_api",
                warnings=[f"Extraction error: {str(e)}"]
            )
