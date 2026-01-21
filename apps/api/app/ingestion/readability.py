import httpx
from bs4 import BeautifulSoup
import bleach
import logging
from trafilatura import extract, extract_metadata
from typing import Optional
from app.ingestion.base import BaseExtractor, ExtractionResult

logger = logging.getLogger(__name__)


class ReadabilityExtractor(BaseExtractor):
    """Extractor using readability/content extraction"""
    
    def can_extract(self, url: str) -> bool:
        """Readability extractor can attempt extraction on any URL"""
        return True
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract main content using readability/content extraction"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; JobCopilot/1.0; +http://jobcopilot.com/bot)"
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                html = response.text
                
                # Use trafilatura for content extraction
                text = extract(html)
                metadata = extract_metadata(html)
                
                # Sanitize HTML
                soup = BeautifulSoup(html, 'html.parser')
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get main content HTML
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and ('content' in x.lower() or 'description' in x.lower()))
                html_content = str(main_content) if main_content else str(soup.body) if soup.body else ""
                
                # Sanitize HTML
                allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span']
                sanitized_html = bleach.clean(html_content, tags=allowed_tags, strip=True)
                
                # Extract title and other metadata
                title = metadata.title if metadata else None
                if not title:
                    title_tag = soup.find('title')
                    title = title_tag.text.strip() if title_tag else None
                
                # Try to find company name (common patterns)
                company_name = None
                # Look for common meta tags
                og_site_name = soup.find('meta', property='og:site_name')
                if og_site_name:
                    company_name = og_site_name.get('content')
                
                # Try to find apply URL
                apply_url = None
                apply_links = soup.find_all('a', string=lambda t: t and 'apply' in t.lower())
                if apply_links:
                    apply_url = apply_links[0].get('href')
                    if apply_url and not apply_url.startswith('http'):
                        # Resolve relative URL
                        from urllib.parse import urljoin
                        apply_url = urljoin(url, apply_url)
                
                description_text = text or sanitized_html or ""
                
                if not description_text:
                    return ExtractionResult(
                        description_text="",
                        extraction_path="readability",
                        warnings=["Could not extract content from page"]
                    )
                
                return ExtractionResult(
                    description_html=sanitized_html,
                    description_text=description_text,
                    title=title,
                    company_name=company_name,
                    apply_url=apply_url or url,
                    extraction_path="readability"
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Readability extraction HTTP error: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="readability",
                warnings=[f"HTTP error: {e.response.status_code}"]
            )
        except Exception as e:
            logger.error(f"Error in readability extraction: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="readability",
                warnings=[f"Extraction error: {str(e)}"]
            )
