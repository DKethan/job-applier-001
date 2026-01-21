"""Provider detection utilities"""
import re
from urllib.parse import urlparse
from typing import Optional, Dict
from enum import Enum


class Provider(str, Enum):
    GREENHOUSE = "GREENHOUSE"
    LEVER = "LEVER"
    ASHBY = "ASHBY"
    SMARTRECRUITERS = "SMARTRECRUITERS"
    WORKDAY = "WORKDAY"
    ORACLE_CX = "ORACLE_CX"
    AVATURE = "AVATURE"
    SUCCESSFACTORS = "SUCCESSFACTORS"
    TALEO = "TALEO"
    ICIMS = "ICIMS"
    PHENOM = "PHENOM"
    UNKNOWN = "UNKNOWN"


PROVIDER_PATTERNS = [
    {
        "provider": Provider.GREENHOUSE,
        "patterns": [
            re.compile(r".*greenhouse\.io.*jobs.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.LEVER,
        "patterns": [
            re.compile(r".*lever\.co.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.ASHBY,
        "patterns": [
            re.compile(r".*ashbyhq\.com.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.SMARTRECRUITERS,
        "patterns": [
            re.compile(r".*smartrecruiters\.com.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.WORKDAY,
        "patterns": [
            re.compile(r".*\.wd\d+\.myworkdayjobs\.com.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.ORACLE_CX,
        "patterns": [
            re.compile(r".*\.fa.*\.oraclecloud\.com.*CandidateExperience.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.AVATURE,
        "patterns": [
            re.compile(r".*\.avature\.net.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.SUCCESSFACTORS,
        "patterns": [
            re.compile(r".*successfactors\.com.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.TALEO,
        "patterns": [
            re.compile(r".*taleo\.net.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.ICIMS,
        "patterns": [
            re.compile(r".*icims\.com.*", re.IGNORECASE),
        ],
    },
    {
        "provider": Provider.PHENOM,
        "patterns": [
            re.compile(r".*phenompeople\.com.*", re.IGNORECASE),
        ],
    },
]


def detect_provider(url_string: str) -> Provider:
    """Detect provider from URL"""
    try:
        url = urlparse(url_string)
        full_path = url.netloc + url.path

        for pattern_config in PROVIDER_PATTERNS:
            for pattern in pattern_config["patterns"]:
                if pattern.search(full_path):
                    return pattern_config["provider"]

        return Provider.UNKNOWN
    except Exception:
        return Provider.UNKNOWN


def extract_greenhouse_ids(url_string: str) -> Optional[Dict[str, str]]:
    """Extract Greenhouse board and job ID from URL"""
    match = re.search(r"greenhouse\.io/([^/]+)/jobs/(\d+)", url_string, re.IGNORECASE)
    if match:
        return {"board": match.group(1), "jobId": match.group(2)}
    return None


def extract_lever_ids(url_string: str) -> Optional[Dict[str, str]]:
    """Extract Lever account and posting ID from URL"""
    match = re.search(r"jobs\.lever\.co/([^/]+)/([^/]+)", url_string, re.IGNORECASE)
    if match:
        return {"account": match.group(1), "postingId": match.group(2)}
    return None


def extract_ashby_ids(url_string: str) -> Optional[Dict[str, str]]:
    """Extract Ashby company and job ID from URL"""
    match = re.search(r"jobs\.ashbyhq\.com/([^/]+)/([^/]+)", url_string, re.IGNORECASE)
    if match:
        return {"company": match.group(1), "jobId": match.group(2)}
    return None


def extract_smartrecruiters_ids(url_string: str) -> Optional[Dict[str, str]]:
    """Extract SmartRecruiters company identifier and posting ID from URL"""
    match = re.search(r"jobs\.smartrecruiters\.com/([^/]+)/([^/]+)", url_string, re.IGNORECASE)
    if match:
        return {"companyIdentifier": match.group(1), "postingId": match.group(2)}
    return None
