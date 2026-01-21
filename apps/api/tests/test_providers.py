"""Unit tests for provider detection"""
import pytest
from app.utils.providers import detect_provider, extract_greenhouse_ids, extract_lever_ids, extract_ashby_ids, extract_smartrecruiters_ids
from app.utils.providers import Provider


def test_detect_greenhouse():
    """Test Greenhouse URL detection"""
    url = "https://job-boards.greenhouse.io/doordashusa/jobs/7264631"
    assert detect_provider(url) == Provider.GREENHOUSE
    
    url2 = "https://boards.greenhouse.io/company/jobs/123"
    assert detect_provider(url2) == Provider.GREENHOUSE


def test_detect_lever():
    """Test Lever URL detection"""
    url = "https://jobs.lever.co/company/posting-id"
    assert detect_provider(url) == Provider.LEVER


def test_detect_ashby():
    """Test Ashby URL detection"""
    url = "https://jobs.ashbyhq.com/company/job-id"
    assert detect_provider(url) == Provider.ASHBY


def test_detect_smartrecruiters():
    """Test SmartRecruiters URL detection"""
    url = "https://jobs.smartrecruiters.com/Company/PostingId"
    assert detect_provider(url) == Provider.SMARTRECRUITERS


def test_extract_greenhouse_ids():
    """Test Greenhouse ID extraction"""
    url = "https://job-boards.greenhouse.io/doordashusa/jobs/7264631"
    ids = extract_greenhouse_ids(url)
    assert ids is not None
    assert ids["board"] == "doordashusa"
    assert ids["jobId"] == "7264631"


def test_extract_lever_ids():
    """Test Lever ID extraction"""
    url = "https://jobs.lever.co/company/posting-id"
    ids = extract_lever_ids(url)
    assert ids is not None
    assert ids["account"] == "company"
    assert ids["postingId"] == "posting-id"


def test_extract_ashby_ids():
    """Test Ashby ID extraction"""
    url = "https://jobs.ashbyhq.com/company/job-id"
    ids = extract_ashby_ids(url)
    assert ids is not None
    assert ids["company"] == "company"
    assert ids["jobId"] == "job-id"


def test_extract_smartrecruiters_ids():
    """Test SmartRecruiters ID extraction"""
    url = "https://jobs.smartrecruiters.com/Company/PostingId"
    ids = extract_smartrecruiters_ids(url)
    assert ids is not None
    assert ids["companyIdentifier"] == "Company"
    assert ids["postingId"] == "PostingId"


def test_detect_unknown():
    """Test unknown URL detection"""
    url = "https://example.com/jobs/123"
    assert detect_provider(url) == Provider.UNKNOWN
