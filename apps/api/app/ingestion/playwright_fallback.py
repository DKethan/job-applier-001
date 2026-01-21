from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import logging
from typing import Optional
from app.ingestion.base import BaseExtractor, ExtractionResult
from app.config import settings

logger = logging.getLogger(__name__)


class PlaywrightFallbackExtractor(BaseExtractor):
    """Fallback extractor using Playwright for JS-rendered pages"""
    
    def can_extract(self, url: str) -> bool:
        """Playwright can attempt extraction if enabled"""
        return settings.playwright_enabled
    
    async def extract(self, url: str) -> ExtractionResult:
        """Extract using Playwright (headless browser)"""
        if not settings.playwright_enabled:
            return ExtractionResult(
                description_text="",
                extraction_path="playwright_fallback",
                warnings=["Playwright not enabled"]
            )
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=settings.playwright_headless)
                page = await browser.new_page()
                
                # Navigate to page
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait for content to load
                await page.wait_for_timeout(2000)
                
                # Get page content
                html = await page.content()
                
                # Try to extract JSON-LD from rendered DOM
                json_ld_data = await page.evaluate("""
                    () => {
                        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                        for (const script of scripts) {
                            try {
                                const data = JSON.parse(script.textContent);
                                if (data['@type'] === 'JobPosting' || 
                                    (Array.isArray(data) && data.some(item => item['@type'] === 'JobPosting'))) {
                                    return data;
                                }
                            } catch (e) {}
                        }
                        return null;
                    }
                """)
                
                # Try to find apply URL
                apply_url = await page.evaluate("""
                    () => {
                        const applyLinks = Array.from(document.querySelectorAll('a'))
                            .filter(a => {
                                const text = a.textContent.toLowerCase();
                                return text.includes('apply') || text.includes('apply now');
                            });
                        return applyLinks.length > 0 ? applyLinks[0].href : null;
                    }
                """)
                
                await browser.close()
                
                # Parse HTML
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract text content
                for script in soup(["script", "style"]):
                    script.decompose()
                
                main_content = soup.find('main') or soup.find('article') or soup.body
                description_text = main_content.get_text(separator='\n', strip=True) if main_content else ""
                description_html = str(main_content) if main_content else ""
                
                # Use JSON-LD data if available
                if json_ld_data:
                    if isinstance(json_ld_data, list):
                        job_posting = next((item for item in json_ld_data if item.get("@type") == "JobPosting"), None)
                    else:
                        job_posting = json_ld_data if json_ld_data.get("@type") == "JobPosting" else None
                    
                    if job_posting:
                        title = job_posting.get("title") or (soup.find('title').text if soup.find('title') else None)
                        company_name = None
                        if job_posting.get("hiringOrganization"):
                            org = job_posting["hiringOrganization"]
                            company_name = org.get("name") if isinstance(org, dict) else str(org)
                        
                        description_text = job_posting.get("description", description_text)
                        
                        return ExtractionResult(
                            description_html=description_html,
                            description_text=description_text,
                            title=title,
                            company_name=company_name,
                            apply_url=apply_url or url,
                            provider_payload={"json_ld": job_posting},
                            extraction_path="playwright"
                        )
                
                # Fallback to extracted content
                title = soup.find('title').text if soup.find('title') else None
                
                if not description_text:
                    return ExtractionResult(
                        description_text="",
                        extraction_path="playwright",
                        warnings=["Could not extract content even with Playwright"]
                    )
                
                return ExtractionResult(
                    description_html=description_html,
                    description_text=description_text,
                    title=title,
                    apply_url=apply_url or url,
                    extraction_path="playwright"
                )
                
        except Exception as e:
            logger.error(f"Error in Playwright extraction: {e}")
            return ExtractionResult(
                description_text="",
                extraction_path="playwright",
                warnings=[f"Playwright extraction error: {str(e)}"]
            )
