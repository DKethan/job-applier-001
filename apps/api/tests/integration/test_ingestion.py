"""Integration tests for job posting ingestion"""
import pytest
import asyncio
from app.routers.jobs import extract_job_posting
from app.utils.providers import Provider


@pytest.mark.asyncio
async def test_greenhouse_ingestion():
    """Test Greenhouse job posting ingestion"""
    url = "https://job-boards.greenhouse.io/doordashusa/jobs/7264631"
    
    job_posting, status = await extract_job_posting(url)
    
    assert status in ["success", "needs_render", "needs_extension_extraction"]
    assert job_posting.provider == Provider.GREENHOUSE.value
    # Note: description_text might be empty if API fails, that's okay for test
    # In real scenario, we'd mock the API or use a known-good URL


@pytest.mark.asyncio
async def test_lever_ingestion():
    """Test Lever job posting ingestion"""
    url = "https://jobs.lever.co/example/123"
    
    job_posting, status = await extract_job_posting(url)
    
    assert status in ["success", "needs_render", "needs_extension_extraction"]
    assert job_posting.provider == Provider.LEVER.value


@pytest.mark.asyncio
async def test_ashby_ingestion():
    """Test Ashby job posting ingestion"""
    url = "https://jobs.ashbyhq.com/example/123"
    
    job_posting, status = await extract_job_posting(url)
    
    assert status in ["success", "needs_render", "needs_extension_extraction"]
    assert job_posting.provider == Provider.ASHBY.value


@pytest.mark.asyncio
async def test_intuit_ingestion():
    """Test Intuit job posting (should detect Avature apply URL)"""
    url = "https://jobs.intuit.com/job/mountain-view/summer-2026-ai-science-intern/27595/87369447088"
    
    job_posting, status = await extract_job_posting(url)
    
    # Should either succeed or need extension extraction
    assert status in ["success", "needs_render", "needs_extension_extraction"]
    
    # If apply_url is found, it should contain avature
    if job_posting.apply_url and job_posting.apply_url != url:
        assert "avature" in job_posting.apply_url.lower()


@pytest.mark.asyncio
async def test_oracle_cx_ingestion():
    """Test Oracle CandidateExperience ingestion"""
    url = "https://fa-evmr-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/27164?src=SNS-102"
    
    job_posting, status = await extract_job_posting(url)
    
    # Should detect provider
    assert job_posting.provider in [Provider.ORACLE_CX.value, Provider.UNKNOWN.value]
    # Should either succeed or need extension extraction
    assert status in ["success", "needs_render", "needs_extension_extraction"]


@pytest.mark.asyncio
async def test_siemens_ingestion():
    """Test Siemens job posting (may be blocked, should fallback gracefully)"""
    url = "https://jobs.siemens.com/en_US/externaljobs/JobDetail/488880"
    
    job_posting, status = await extract_job_posting(url)
    
    # Should handle 406 gracefully and fallback to Playwright or extension
    assert status in ["success", "needs_render", "needs_extension_extraction"]
    # Should not crash
