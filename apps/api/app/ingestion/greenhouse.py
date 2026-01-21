import httpx
from typing import Optional
from urllib.parse import urlparse
import re
from app.ingestion.base import BaseExtractor, ExtractionResult
from app.schemas.application import ApplicationField, ApplicationFieldType, SelectOption
from app.utils.providers import extract_greenhouse_ids
from app.utils.app_logger import app_logger


class GreenhouseExtractor(BaseExtractor):
    """Extractor for Greenhouse job postings"""
    
    def can_extract(self, url: str) -> bool:
        """Check if URL is a Greenhouse job posting"""
        try:
            parsed = urlparse(url)
            return bool(re.match(r'.*greenhouse\.io.*jobs.*', parsed.netloc + parsed.path, re.IGNORECASE))
        except Exception:
            return False
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract from Greenhouse public API"""
        ids = extract_greenhouse_ids(url)
        if not ids:
            return ExtractionResult(
                description_text="",
                extraction_path="greenhouse_api",
                warnings=["Could not parse Greenhouse URL"]
            )
        
        board = ids["board"]
        job_id = ids["jobId"]
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{job_id}?questions=true"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url)
                response.raise_for_status()
                data = response.json()
                
                # Extract fields
                description_html = data.get("content", "")
                description_text = self._html_to_text(description_html)
                title = data.get("title")
                company_name = data.get("departments", [{}])[0].get("name") if data.get("departments") else None
                location = data.get("location", {}).get("name") if data.get("location") else None
                
                # Get apply URL
                apply_url = f"https://boards.greenhouse.io/{board}/jobs/{job_id}"
                if data.get("absolute_url"):
                    apply_url = data["absolute_url"]
                
                # Extract questions as application form schema
                application_form_schema = []
                questions = data.get("questions", [])
                for idx, q in enumerate(questions):
                    field = self._parse_question(q, idx)
                    if field:
                        application_form_schema.append(field)
                
                return ExtractionResult(
                    description_html=description_html,
                    description_text=description_text,
                    title=title,
                    company_name=company_name,
                    location=location,
                    apply_url=apply_url,
                    application_form_schema=application_form_schema,
                    provider_payload=data,
                    extraction_path="greenhouse_api"
                )
                
        except httpx.HTTPStatusError as e:
            app_logger.log_error(f"Greenhouse API error: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="greenhouse_api",
                warnings=[f"HTTP error: {e.response.status_code}"]
            )
        except Exception as e:
            app_logger.log_error(f"Error extracting from Greenhouse: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="greenhouse_api",
                warnings=[f"Extraction error: {str(e)}"]
            )
    
    def _html_to_text(self, html: str) -> str:
        """Simple HTML to text conversion"""
        if not html:
            return ""
        # Remove HTML tags (basic implementation)
        import re
        text = re.sub(r'<[^>]+>', '', html)
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()
    
    def _parse_question(self, question: dict, idx: int) -> Optional[ApplicationField]:
        """Parse Greenhouse question into ApplicationField"""
        label = question.get("label", f"Question {idx + 1}")
        required = question.get("required", False)
        field_type = question.get("type", "text")
        options = question.get("options", [])
        
        # Map Greenhouse types to our types
        type_mapping = {
            "short_text": ApplicationFieldType.text,
            "long_text": ApplicationFieldType.textarea,
            "email": ApplicationFieldType.email,
            "phone": ApplicationFieldType.tel,
            "url": ApplicationFieldType.url,
            "multi_select": ApplicationFieldType.select,
            "single_select": ApplicationFieldType.select,
            "date": ApplicationFieldType.date,
            "file": ApplicationFieldType.file,
        }
        
        app_type = type_mapping.get(field_type, ApplicationFieldType.unknown)
        
        # Build select options
        select_options = None
        if app_type in [ApplicationFieldType.select, ApplicationFieldType.radio]:
            select_options = [
                SelectOption(value=str(opt.get("id", "")), label=opt.get("label", ""))
                for opt in options
            ]
        
        key = f"question_{idx}"
        
        return ApplicationField(
            key=key,
            label=label,
            type=app_type,
            required=required,
            options=select_options,
            source_hint="greenhouse_questions"
        )
