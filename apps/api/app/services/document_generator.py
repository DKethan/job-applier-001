import uuid
from pathlib import Path
from typing import Optional, Any
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from app.config import settings
from app.schemas.profile import ProfileSchema
from app.schemas.tailor import TailorResponse, SuggestedBullet
from app.utils.encryption import encryption_service
from app.utils.app_logger import app_logger
import json
import os


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
        job_posting: Any,
        original_profile_id: Optional[str] = None
    ) -> tuple[str, str, Optional[str], Optional[str]]:
        """Generate tailored application documents, return file IDs

        Returns: (docx_resume_id, pdf_resume_id, cover_letter_docx_id, application_package_id)

        Uses pure Python libraries:
        - python-docx for DOCX generation
        - ReportLab for PDF generation (no system dependencies)
        """

        # Generate DOCX resume (always available)
        docx_file_id = await self._generate_docx(profile, tailoring, original_profile_id)

        # Generate PDF resume (may be unavailable if ReportLab fails)
        pdf_file_id = await self._generate_pdf(profile, tailoring, original_profile_id)

        # Generate cover letter DOCX
        cover_letter_file_id = await self._generate_cover_letter_docx(profile, tailoring, original_profile_id)

        # Generate application package (resume + cover letter + summary)
        package_file_id = await self._generate_application_package_docx(profile, tailoring, job_posting, original_profile_id)

        # If PDF generation failed (returned None), use DOCX file_id as fallback
        # The download endpoint will serve DOCX when PDF is requested
        if pdf_file_id is None:
            pdf_file_id = docx_file_id

        return docx_file_id, pdf_file_id, cover_letter_file_id, package_file_id

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
        """Generate PDF using ReportLab (pure Python, no system dependencies)"""
        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}.pdf"

        try:
            # Create PDF using ReportLab
            doc = SimpleDocTemplate(str(file_path), pagesize=letter)
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12,
                alignment=TA_CENTER
            )

            section_style = ParagraphStyle(
                'Section',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=8,
                borderWidth=1,
                borderColor='black',
                borderPadding=4
            )

            job_title_style = ParagraphStyle(
                'JobTitle',
                parent=styles['Normal'],
                fontSize=12,
                fontName='Helvetica-Bold',
                spaceAfter=4
            )

            company_style = ParagraphStyle(
                'Company',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=2
            )

            date_style = ParagraphStyle(
                'Date',
                parent=styles['Normal'],
                fontSize=10,
                textColor='gray',
                spaceAfter=8
            )

            bullet_style = ParagraphStyle(
                'Bullet',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=20,
                spaceAfter=2
            )

            # Build PDF content
            content = []

            # Header - Name
            full_name = f"{profile.basics.firstName} {profile.basics.lastName}".strip()
            content.append(Paragraph(full_name, title_style))

            # Contact info
            contact_parts = []
            if profile.basics.email:
                contact_parts.append(profile.basics.email)
            if profile.basics.phone:
                contact_parts.append(profile.basics.phone)
            if profile.basics.location:
                contact_parts.append(profile.basics.location)

            if contact_parts:
                contact_text = " | ".join(contact_parts)
                contact_style = ParagraphStyle(
                    'Contact',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=TA_CENTER,
                    spaceAfter=20
                )
                content.append(Paragraph(contact_text, contact_style))

            # Professional Summary
            if profile.basics.summary:
                summary_style = ParagraphStyle(
                    'Summary',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=15
                )
                content.append(Paragraph(profile.basics.summary, summary_style))

            # Work Experience
            if profile.work_experience:
                content.append(Paragraph("Work Experience", section_style))

                for exp in profile.work_experience:
                    # Find tailored bullets for this role
                    tailored_bullets = [
                        tb.tailored for tb in tailoring.suggested_bullets
                        if tb.role_id and exp.company.lower() in tb.role_id.lower()
                    ]
                    bullets_to_use = tailored_bullets if tailored_bullets else exp.bullets

                    # Job title and company
                    content.append(Paragraph(exp.title, job_title_style))
                    content.append(Paragraph(exp.company, company_style))

                    # Date range
                    start_date = exp.startDate or ''
                    end_date = exp.endDate or 'Present'
                    date_text = f"{start_date} - {end_date}"
                    content.append(Paragraph(date_text, date_style))

                    # Location
                    if exp.location:
                        content.append(Paragraph(f"Location: {exp.location}", bullet_style))

                    # Technologies
                    if exp.technologies and len(exp.technologies) > 0:
                        tech_text = f"Technologies: {', '.join(exp.technologies)}"
                        content.append(Paragraph(tech_text, bullet_style))

                    # Bullets
                    if bullets_to_use:
                        for bullet in bullets_to_use:
                            content.append(Paragraph(f"• {bullet}", bullet_style))

                    content.append(Spacer(1, 8))  # Add space between jobs

            # Education
            if profile.education:
                content.append(Paragraph("Education", section_style))

                for edu in profile.education:
                    degree_text = edu.degree
                    if edu.field:
                        degree_text += f" in {edu.field}"

                    content.append(Paragraph(degree_text, job_title_style))
                    content.append(Paragraph(edu.school, company_style))

                    # Date range
                    start_date = edu.startDate or ''
                    end_date = edu.endDate or ''
                    if start_date or end_date:
                        date_text = f"{start_date} - {end_date}".strip(' - ')
                        content.append(Paragraph(date_text, date_style))

                    # GPA
                    if edu.gpa:
                        content.append(Paragraph(f"GPA: {edu.gpa}", bullet_style))

                    # Bullets
                    if edu.bullets:
                        for bullet in edu.bullets:
                            content.append(Paragraph(f"• {bullet}", bullet_style))

                    content.append(Spacer(1, 6))

            # Projects
            if profile.projects:
                content.append(Paragraph("Projects", section_style))

                for project in profile.projects:
                    content.append(Paragraph(project.name, job_title_style))

                    if project.description:
                        content.append(Paragraph(project.description, styles['Normal']))

                    # Technologies
                    if project.tech and len(project.tech) > 0:
                        tech_text = f"Technologies: {', '.join(project.tech)}"
                        content.append(Paragraph(tech_text, bullet_style))

                    # Outcomes
                    if project.outcomes:
                        for outcome in project.outcomes:
                            content.append(Paragraph(f"• {outcome}", bullet_style))

                    content.append(Spacer(1, 6))

            # Skills
            if profile.skills:
                content.append(Paragraph("Skills", section_style))

                # Group skills by category
                skills_by_category = {}
                for skill in profile.skills:
                    category = skill.category or 'Technical Skills'
                    if category not in skills_by_category:
                        skills_by_category[category] = []
                    skill_text = f"{skill.name} ({skill.level})" if skill.level else skill.name
                    skills_by_category[category].append(skill_text)

                for category, skills in skills_by_category.items():
                    content.append(Paragraph(f"**{category}:** {', '.join(skills)}", bullet_style))

            # Languages
            if profile.languages:
                content.append(Paragraph("Languages", section_style))
                for lang in profile.languages:
                    proficiency = f" ({lang.proficiency})" if lang.proficiency else ""
                    content.append(Paragraph(f"• {lang.name}{proficiency}", bullet_style))

            # Build PDF
            doc.build(content)
            app_logger.log_info(f"PDF generated successfully using ReportLab: {file_id}")
            return file_id

        except Exception as e:
            app_logger.log_error(f"ReportLab PDF generation error: {e}")
            app_logger.log_warning("PDF generation failed. DOCX will be served instead.")
            return None

    async def _generate_cover_letter_docx(
        self,
        profile: ProfileSchema,
        tailoring: TailorResponse,
        original_profile_id: Optional[str]
    ) -> Optional[str]:
        """Generate cover letter DOCX"""
        if not tailoring.cover_letter_text:
            app_logger.log_info("No cover letter text available, skipping cover letter generation")
            return None

        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}_cover_letter.docx"

        try:
            doc = Document()

            # Set margins
            sections = doc.sections
            for section in sections:
                section.top_margin = Inches(1)
                section.bottom_margin = Inches(1)
                section.left_margin = Inches(1)
                section.right_margin = Inches(1)

            # Header - Contact info
            header = doc.add_paragraph()
            header.alignment = 1  # Center
            run = header.add_run(f"{profile.basics.firstName} {profile.basics.lastName}")
            run.bold = True
            run.font.size = Pt(14)

            # Contact info
            contact_info = []
            if profile.basics.email:
                contact_info.append(profile.basics.email)
            if profile.basics.phone:
                contact_info.append(profile.basics.phone)
            if profile.basics.location:
                contact_info.append(profile.basics.location)

            if contact_info:
                contact_para = doc.add_paragraph()
                contact_para.alignment = 1  # Center
                contact_run = contact_para.add_run(" | ".join(contact_info))
                contact_run.font.size = Pt(10)

            # Add spacing
            doc.add_paragraph()

            # Date
            import datetime
            date_para = doc.add_paragraph()
            date_run = date_para.add_run(datetime.date.today().strftime("%B %d, %Y"))
            date_run.font.size = Pt(10)

            # Add spacing
            doc.add_paragraph()

            # Hiring manager greeting (generic)
            greeting = doc.add_paragraph()
            greeting_run = greeting.add_run("Dear Hiring Manager,")
            greeting_run.font.size = Pt(11)

            # Cover letter content
            for paragraph in tailoring.cover_letter_text.split('\n\n'):
                if paragraph.strip():
                    para = doc.add_paragraph()
                    run = para.add_run(paragraph.strip())
                    run.font.size = Pt(11)

            # Closing
            doc.add_paragraph()
            closing = doc.add_paragraph()
            closing_run = closing.add_run("Sincerely,")
            closing_run.font.size = Pt(11)

            # Name
            doc.add_paragraph()
            name_para = doc.add_paragraph()
            name_run = name_para.add_run(f"{profile.basics.firstName} {profile.basics.lastName}")
            name_run.bold = True
            name_run.font.size = Pt(11)

            # Save document
            doc.save(str(file_path))
            app_logger.log_info(f"Cover letter DOCX generated: {file_id}")
            return file_id

        except Exception as e:
            app_logger.log_error(f"Cover letter DOCX generation error: {e}")
            return None

    async def _generate_application_package_docx(
        self,
        profile: ProfileSchema,
        tailoring: TailorResponse,
        job_posting: Any,
        original_profile_id: Optional[str]
    ) -> Optional[str]:
        """Generate complete application package DOCX (resume + cover letter + summary)"""
        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}_application_package.docx"

        try:
            doc = Document()

            # Title page
            title = doc.add_heading('Job Application Package', 0)
            title.alignment = 1  # Center

            company = job_posting.company_name or "Company"
            position = job_posting.title or "Position"

            subtitle = doc.add_paragraph()
            subtitle.alignment = 1
            sub_run = subtitle.add_run(f"Application for {position} at {company}")
            sub_run.bold = True

            # Applicant info
            doc.add_heading('Applicant Information', level=1)
            info_table = doc.add_table(rows=4, cols=2)
            info_table.style = 'Table Grid'

            cells = info_table.rows[0].cells
            cells[0].text = 'Name:'
            cells[1].text = f"{profile.basics.firstName} {profile.basics.lastName}"

            cells = info_table.rows[1].cells
            cells[0].text = 'Email:'
            cells[1].text = profile.basics.email or 'N/A'

            cells = info_table.rows[2].cells
            cells[0].text = 'Phone:'
            cells[1].text = profile.basics.phone or 'N/A'

            cells = info_table.rows[3].cells
            cells[0].text = 'Location:'
            cells[1].text = profile.basics.location or 'N/A'

            # Job details
            doc.add_heading('Position Details', level=1)
            job_table = doc.add_table(rows=3, cols=2)
            job_table.style = 'Table Grid'

            cells = job_table.rows[0].cells
            cells[0].text = 'Position:'
            cells[1].text = position

            cells = job_table.rows[1].cells
            cells[0].text = 'Company:'
            cells[1].text = company

            cells = job_table.rows[2].cells
            cells[0].text = 'Location:'
            cells[1].text = job_posting.location or 'Not specified'

            # Job description summary
            doc.add_heading('Job Description Summary', level=1)
            if tailoring.jd_summary:
                jd_para = doc.add_paragraph()
                jd_para.add_run(tailoring.jd_summary)

            # Required skills
            doc.add_heading('Required Skills', level=1)
            if tailoring.skills_required:
                skills_para = doc.add_paragraph()
                skills_para.add_run(tailoring.skills_required)

            # Suggested resume bullets
            doc.add_heading('Tailored Resume Highlights', level=1)
            for bullet in tailoring.suggested_bullets:
                bullet_para = doc.add_paragraph()
                bullet_para.add_run(f"• {bullet.tailored}")

            # Cover letter
            if tailoring.cover_letter_text:
                doc.add_heading('Cover Letter', level=1)
                for paragraph in tailoring.cover_letter_text.split('\n\n'):
                    if paragraph.strip():
                        para = doc.add_paragraph()
                        para.add_run(paragraph.strip())

            # Resume section marker
            doc.add_page_break()
            resume_marker = doc.add_heading('RESUME FOLLOWS ON NEXT PAGE', level=1)
            resume_marker.alignment = 1

            app_logger.log_info(f"Application package DOCX generated: {file_id}")
            doc.save(str(file_path))
            return file_id

        except Exception as e:
            app_logger.log_error(f"Application package DOCX generation error: {e}")
            return None

document_generator = DocumentGenerator()
