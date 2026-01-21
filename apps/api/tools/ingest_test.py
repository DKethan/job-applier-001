#!/usr/bin/env python3
"""CLI tool to test job posting ingestion"""
import asyncio
import sys
import argparse
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routers.jobs import extract_job_posting
from app.utils.providers import detect_provider

async def test_ingest(url: str):
    """Test ingestion for a URL"""
    print(f"Testing ingestion for: {url}\n")
    
    # Detect provider
    provider = detect_provider(url)
    print(f"Detected provider: {provider.value}\n")
    
    # Extract job posting
    print("Extracting job posting...")
    try:
        job_posting, status = await extract_job_posting(url)
        
        print(f"\nStatus: {status}")
        print(f"Title: {job_posting.title or 'N/A'}")
        print(f"Company: {job_posting.company_name or 'N/A'}")
        print(f"Location: {job_posting.location or 'N/A'}")
        print(f"Apply URL: {job_posting.apply_url or 'N/A'}")
        print(f"\nDescription (first 300 chars):")
        print(job_posting.description_text[:300] if job_posting.description_text else "No description extracted")
        
        if hasattr(job_posting, 'raw') and job_posting.raw:
            raw_data = job_posting.raw if isinstance(job_posting.raw, dict) else job_posting.raw.dict()
            if raw_data.get("warnings"):
                print(f"\nWarnings: {', '.join(raw_data.get('warnings', []))}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Test job posting ingestion")
    parser.add_argument("--url", required=True, help="Job posting URL to test")
    args = parser.parse_args()
    
    # Run async test
    asyncio.run(test_ingest(args.url))


if __name__ == "__main__":
    main()
