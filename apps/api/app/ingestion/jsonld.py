import httpx
from bs4 import BeautifulSoup
import json
import logging
from typing import Optional
from app.ingestion.base import BaseExtractor, ExtractionResult

logger = logging.getLogger(__name__)


class JSONLDExtractor(BaseExtractor):
    """Extractor for schema.org JobPosting JSON-LD"""
    
    def can_extract(self, url: str) -> bool:
        """JSON-LD extractor can attempt extraction on any URL"""
        return True
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract job posting from JSON-LD"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; JobCopilot/1.0; +http://jobcopilot.com/bot)"
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                html = response.text
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find JSON-LD scripts
                json_ld_scripts = soup.find_all('script', type='application/ld+json')
                
                job_posting_data = None
                for script in json_ld_scripts:
                    try:
                        data = json.loads(script.string)
                        # Handle both single objects and arrays
                        if isinstance(data, list):
                            for item in data:
                                if item.get("@type") == "JobPosting":
                                    job_posting_data = item
                                    break
                        elif data.get("@type") == "JobPosting":
                            job_posting_data = data
                            break
                    except json.JSONDecodeError:
                        continue
                
                if not job_posting_data:
                    return ExtractionResult(
                        description_text="",
                        extraction_path="jsonld",
                        warnings=["No JobPosting JSON-LD found"]
                    )
                
                # Extract fields from JobPosting schema
                description_html = job_posting_data.get("description", "")
                description_text = description_html  # JSON-LD usually has plain text
                title = job_posting_data.get("title")
                company_name = None
                if job_posting_data.get("hiringOrganization"):
                    company_name = job_posting_data["hiringOrganization"].get("name") if isinstance(job_posting_data["hiringOrganization"], dict) else str(job_posting_data["hiringOrganization"])
                
                location = None
                if job_posting_data.get("jobLocation"):
                    loc = job_posting_data["jobLocation"]
                    if isinstance(loc, dict):
                        if loc.get("address"):
                            addr = loc["address"]
                            parts = [addr.get("addressLocality"), addr.get("addressRegion"), addr.get("addressCountry")]
                            location = ", ".join([p for p in parts if p])
                
                # Get apply URL
                apply_url = job_posting_data.get("jobLocationType") or url
                if job_posting_data.get("directApply"):
                    # Some JSON-LD includes direct apply URL
                    pass
                
                # Employment type
                employment_type = job_posting_data.get("employmentType")
                
                return ExtractionResult(
                    description_html=description_html,
                    description_text=description_text,
                    title=title,
                    company_name=company_name,
                    location=location,
                    employment_type=employment_type,
                    apply_url=apply_url or url,
                    provider_payload=job_posting_data,
                    extraction_path="jsonld"
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"JSON-LD extraction HTTP error: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="jsonld",
                warnings=[f"HTTP error: {e.response.status_code}"]
            )
        except Exception as e:
            logger.error(f"Error extracting JSON-LD: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="jsonld",
                warnings=[f"Extraction error: {str(e)}"]
            )
