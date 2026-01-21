import uuid
from pathlib import Path
from typing import Optional
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.config import settings
from app.schemas.profile import ProfileSchema
from app.schemas.tailor import TailorResponse, SuggestedBullet
from app.utils.encryption import encryption_service
from app.utils.app_logger import app_logger
import json
import os

# WeasyPrint will be imported lazily when needed (requires system libraries on macOS)


class DocumentGenerator:
    """Generate tailored resume documents (DOCX and PDF)"""

    def __init__(self):
        # Convert to absolute path (handles relative paths like ./data/uploads)
        upload_path = Path(settings.storage_local_dir)
        if not upload_path.is_absolute():
            # Make relative to the API directory
            api_dir = Path(__file__).parent.parent.parent  # Go up from services -> app -> api
            upload_path = api_dir / upload_path
        self.upload_dir = upload_path.resolve()
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def generate_tailored_resume(
        self,
        profile: ProfileSchema,
        tailoring: TailorResponse,
        original_profile_id: Optional[str] = None
    ) -> tuple[str, str]:
        """Generate tailored resume DOCX and PDF, return file IDs
        
        Note: PDF generation requires WeasyPrint system libraries (Cairo, Pango).
        If unavailable, PDF download will serve DOCX instead.
        """
        
        # Generate DOCX (always available)
        docx_file_id = await self._generate_docx(profile, tailoring, original_profile_id)
        
        # Generate PDF (may be unavailable if WeasyPrint system libs not installed)
        pdf_file_id = await self._generate_pdf(profile, tailoring, original_profile_id)
        
        # If PDF generation failed (returned None), use DOCX file_id as fallback
        # Download endpoint will serve DOCX when PDF is requested
        if pdf_file_id is None:
            pdf_file_id = docx_file_id
        
        return docx_file_id, pdf_file_id

    async def _generate_docx(
        self,
        profile: ProfileSchema,
        tailoring: TailorResponse,
        original_profile_id: Optional[str]
    ) -> str:
        """Generate tailored resume DOCX"""
        doc = Document()
        
        # Set margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)
        
        # Header - Name and contact info
        header = doc.add_paragraph()
        name_run = header.add_run(f"{profile.basics.firstName} {profile.basics.lastName}")
        name_run.font.size = Pt(18)
        name_run.bold = True
        header.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        contact_info = []
        if profile.basics.email:
            contact_info.append(profile.basics.email)
        if profile.basics.phone:
            contact_info.append(profile.basics.phone)
        if profile.basics.location:
            contact_info.append(profile.basics.location)
        
        if contact_info:
            contact_para = doc.add_paragraph(" | ".join(contact_info))
            contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Links
        if profile.basics.links:
            links_text = " | ".join([f"{link.label or link.type}: {link.url}" for link in profile.basics.links])
            links_para = doc.add_paragraph(links_text)
            links_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()  # Spacing
        
        # Work Experience
        if profile.work_experience:
            doc.add_paragraph("WORK EXPERIENCE", style="Heading 1")
            for exp in profile.work_experience:
                # Find tailored bullets
                tailored_bullets = [
                    tb for tb in tailoring.suggested_bullets
                    if tb.role_id and exp.company in tb.role_id
                ]
                
                # Title and company
                title_para = doc.add_paragraph()
                title_run = title_para.add_run(f"{exp.title} at {exp.company}")
                title_run.bold = True
                title_run.font.size = Pt(12)
                
                # Date range
                date_text = f"{exp.startDate} - {exp.endDate or 'Present'}"
                if exp.location:
                    date_text += f" | {exp.location}"
                date_para = doc.add_paragraph(date_text)
                date_para.italic = True
                
                # Bullets - use tailored if available
                bullets_to_use = []
                if tailored_bullets:
                    bullets_to_use = [tb.tailored for tb in tailored_bullets]
                else:
                    bullets_to_use = exp.bullets
                
                for bullet in bullets_to_use:
                    bullet_para = doc.add_paragraph(bullet, style="List Bullet")
                
                doc.add_paragraph()  # Spacing
        
        # Education
        if profile.education:
            doc.add_paragraph("EDUCATION", style="Heading 1")
            for edu in profile.education:
                edu_para = doc.add_paragraph()
                edu_run = edu_para.add_run(f"{edu.degree}")
                if edu.field:
                    edu_run.add_text(f" in {edu.field}")
                edu_run.bold = True
                edu_run.font.size = Pt(12)
                
                school_para = doc.add_paragraph(edu.school)
                if edu.gpa:
                    gpa_para = doc.add_paragraph(f"GPA: {edu.gpa}")
                    gpa_para.italic = True
                
                doc.add_paragraph()  # Spacing
        
        # Projects
        if profile.projects:
            doc.add_paragraph("PROJECTS", style="Heading 1")
            for proj in profile.projects:
                proj_para = doc.add_paragraph()
                proj_run = proj_para.add_run(proj.name)
                proj_run.bold = True
                if proj.link:
                    proj_run.add_text(f" - {proj.link}")
                
                if proj.description:
                    desc_para = doc.add_paragraph(proj.description)
                    desc_para.italic = True
                
                for bullet in proj.bullets:
                    bullet_para = doc.add_paragraph(bullet, style="List Bullet")
                
                doc.add_paragraph()  # Spacing
        
        # Skills
        if profile.skills:
            doc.add_paragraph("SKILLS", style="Heading 1")
            skills_text = ", ".join([f"{s.name}" + (f" ({s.level})" if s.level else "") for s in profile.skills])
            skills_para = doc.add_paragraph(skills_text)
        
        # Save DOCX
        docx_file_id = str(uuid.uuid4())
        docx_file_path = self.upload_dir / f"{docx_file_id}.docx"
        doc.save(str(docx_file_path))
        
        return docx_file_id

    async def _generate_pdf(
        self,
        profile: ProfileSchema,
        tailoring: TailorResponse,
        original_profile_id: Optional[str]
    ) -> Optional[str]:
        """Generate PDF from HTML (fallback: use WeasyPrint)"""
        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}.pdf"
        
        # Try to import and use WeasyPrint (lazy import to avoid startup errors)
        try:
            from weasyprint import HTML
            html_content = self._generate_html_resume(profile, tailoring)
            HTML(string=html_content).write_pdf(str(file_path))
            app_logger.log_info(f"PDF generated successfully: {file_id}")
            return file_id
        except OSError as e:
            app_logger.log_warning(f"WeasyPrint requires system libraries: {e}")
            app_logger.log_warning("PDF generation unavailable. DOCX will be served instead.")
            app_logger.log_info("To enable PDF generation, install: brew install cairo pango gdk-pixbuf libffi")
        except ImportError as e:
            app_logger.log_warning(f"WeasyPrint not available: {e}")
        except Exception as e:
            app_logger.log_error(f"PDF generation error: {e}")
        
        # Fallback: PDF generation unavailable
        # Return None to indicate PDF wasn't generated
        # The download endpoint will serve DOCX when PDF is requested
        app_logger.log_info("PDF generation skipped - system libraries not available. DOCX will be served instead.")
        return None  # Indicate PDF wasn't generated

    def _generate_html_resume(
        self,
        profile: ProfileSchema,
        tailoring: TailorResponse
    ) -> str:
        """Generate HTML version of resume"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{ text-align: center; font-size: 24px; margin-bottom: 10px; }}
                .contact {{ text-align: center; margin-bottom: 20px; }}
                .section {{ margin-top: 20px; }}
                .section-title {{ font-size: 18px; font-weight: bold; border-bottom: 2px solid #333; padding-bottom: 5px; }}
                .job-title {{ font-weight: bold; font-size: 14px; }}
                .date {{ font-style: italic; color: #666; }}
                ul {{ margin: 10px 0; padding-left: 20px; }}
            </style>
        </head>
        <body>
            <h1>{profile.basics.firstName.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")} {profile.basics.lastName.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</h1>
            <div class="contact">
                {profile.basics.email or ""} | {profile.basics.phone or ""} | {profile.basics.location or ""}
            </div>
            
            <div class="section">
                <div class="section-title">Work Experience</div>
        """
        
        for exp in profile.work_experience:
            tailored_bullets = [
                tb.tailored for tb in tailoring.suggested_bullets
                if tb.role_id and exp.company in tb.role_id
            ]
            bullets_to_use = tailored_bullets if tailored_bullets else exp.bullets
            
            html += f"""
                <div class="job-title">{exp.title} at {exp.company}</div>
                <div class="date">{exp.startDate} - {exp.endDate or 'Present'}</div>
                <ul>
            """
            for bullet in bullets_to_use:
                # Escape HTML in bullet
                escaped_bullet = bullet.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                html += f"<li>{escaped_bullet}</li>"
            html += "</ul>"
        
        html += """
            </div>
            
            <div class="section">
                <div class="section-title">Education</div>
        """
        
        for edu in profile.education:
            html += f"""
                <div class="job-title">{edu.degree}{f' in {edu.field}' if edu.field else ''}</div>
                <div>{edu.school}</div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html


document_generator = DocumentGenerator()
