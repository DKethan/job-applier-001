import json
from typing import Dict, Any
from openai import OpenAI
from app.config import settings
from app.schemas.profile import ProfileSchema
from app.schemas.job_posting import JobPostingResponse
from app.schemas.tailor import TailorResponse, TailorRequest, SuggestedBullet, Gap, AutofillAnswers
from app.utils.app_logger import app_logger


class TailoringService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def tailor_resume(
        self,
        job_posting: JobPostingResponse,
        profile: ProfileSchema
    ) -> TailorResponse:
        """Generate tailored resume content and cover letter"""
        if not self.client:
            raise ValueError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        # Build prompt
        job_description = job_posting.description_text
        profile_json = json.dumps(profile.model_dump(), indent=2)

        prompt = f"""You are a resume tailoring expert. Given a job description and a candidate's profile, generate:
1. A short JD summary (2-3 sentences)
2. List of required skills (extracted from JD)
3. Skill/experience gaps (what's missing - do NOT fabricate, only note what's genuinely missing)
4. Tailored bullet points for each role/project (rewrite wording to match JD keywords, but do NOT change facts or add fake experiences)
5. A short cover letter draft (2-3 paragraphs)
6. Autofill answers for common application form fields

IMPORTANT:
- Do NOT fabricate employers, education, or experiences
- Only rewrite wording of existing bullets to match job keywords
- If information is missing (e.g., visa status), set to null or empty string
- Autofill answers should use data from the profile only

Job Description:
{job_description}

Candidate Profile:
{profile_json}

Return JSON with this structure:
{{
  "jd_summary": "string",
  "skills_required": ["skill1", "skill2", ...],
  "gaps": [
    {{"skill": "optional", "experience": "optional", "note": "string"}}
  ],
  "suggested_bullets": [
    {{"role_id": "optional reference", "original": "string", "tailored": "string"}}
  ],
  "cover_letter_text": "string",
  "autofill_answers": {{
    "legalName": "string (full name from profile)",
    "email": "string",
    "phone": "string",
    "linkedin": "string (from links)",
    "github": "string (from links)",
    "portfolio": "string (from links)",
    "workAuth": "string (from preferences)",
    "visaStatus": "string (from preferences)",
    "salaryExpectation": "null or empty if not available",
    "availability": "null or empty if not available",
    "relocation": "string (yes/no from preferences)",
    "remote": "string (yes/no from preferences)"
  }}
}}

Return only valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a resume tailoring expert. Always return valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            content = response.choices[0].message.content
            data = json.loads(content)

            # Parse suggested bullets
            suggested_bullets = [
                SuggestedBullet(**bullet) for bullet in data.get("suggested_bullets", [])
            ]

            # Parse gaps
            gaps = [
                Gap(**gap) for gap in data.get("gaps", [])
            ]

            # Parse autofill answers
            autofill_data = data.get("autofill_answers", {})
            extra = {k: v for k, v in autofill_data.items() if k not in [
                "legalName", "email", "phone", "linkedin", "github", "portfolio",
                "workAuth", "visaStatus", "salaryExpectation", "availability", "relocation", "remote"
            ]}
            autofill_answers = AutofillAnswers(
                legalName=autofill_data.get("legalName"),
                email=autofill_data.get("email"),
                phone=autofill_data.get("phone"),
                linkedin=autofill_data.get("linkedin"),
                github=autofill_data.get("github"),
                portfolio=autofill_data.get("portfolio"),
                workAuth=autofill_data.get("workAuth"),
                visaStatus=autofill_data.get("visaStatus"),
                salaryExpectation=autofill_data.get("salaryExpectation"),
                availability=autofill_data.get("availability"),
                relocation=autofill_data.get("relocation"),
                remote=autofill_data.get("remote"),
                extra=extra
            )

            return TailorResponse(
                jd_summary=data.get("jd_summary", ""),
                skills_required=data.get("skills_required", []),
                gaps=gaps,
                suggested_bullets=suggested_bullets,
                cover_letter_text=data.get("cover_letter_text", ""),
                autofill_answers=autofill_answers,
                tailored_resume_docx_url="",  # Will be set by document generator
                tailored_resume_pdf_url="",   # Will be set by document generator
            )

        except json.JSONDecodeError as e:
            app_logger.log_error(f"Invalid JSON from LLM: {e}")
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            app_logger.log_error(f"Error calling LLM for tailoring: {e}")
            raise


tailoring_service = TailoringService()
