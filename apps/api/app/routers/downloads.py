from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from pymongo.database import Database
from pathlib import Path
from bson import ObjectId
from app.database import get_db
from app.models.file_storage import FileStorage
from app.models.user import User
from app.routers.auth import get_current_user
from app.config import settings
from app.utils.encryption import encryption_service
from app.utils.app_logger import app_logger
import os
import zipfile
import io

router = APIRouter()


@router.get("/package/{file_id}")
async def download_package(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Download a complete application package (ZIP)"""
    app_logger.log_info(f"Package download request for file_id: {file_id} by user: {current_user.id}")

    # Find the job application record to get the specific file IDs
    job_app = db.job_applications.find_one({
        "user_id": str(current_user.id),
        "file_ids.package_zip": file_id
    })

    if not job_app or "file_ids" not in job_app:
        app_logger.log_error(f"No job application found for package_id: {file_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Package not found"
        )

    resume_file_id = job_app["file_ids"].get("resume_docx")
    cover_file_id = job_app["file_ids"].get("cover_letter_docx")

    if not resume_file_id:
        app_logger.log_error(f"No resume file ID found for package: {file_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found"
        )

    # Construct upload directory
    upload_path = Path(settings.storage_local_dir)
    if not upload_path.is_absolute():
        api_dir = Path(__file__).parent.parent.parent  # Go up from routers -> app -> api
        upload_path = api_dir / upload_path
    upload_dir = upload_path.resolve()

    # Generate ZIP with the specific files for this tailoring request
    app_logger.log_info(f"Generating ZIP for package {file_id}: resume={resume_file_id}, cover={cover_file_id}")
    return await _generate_zip_for_tailoring(resume_file_id, cover_file_id, upload_dir)

@router.get("/{file_id}")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Download a file (verify ownership, decrypt if needed)"""
    app_logger.log_info(f"Download request for file_id: {file_id} by user: {current_user.id}")

    # Check if file exists in storage
    # First, try to find in FileStorage collection
    try:
        file_doc = db.file_storage.find_one({"_id": ObjectId(file_id)})
    except Exception:
        file_doc = None
    
    file_storage = FileStorage.from_dict(file_doc) if file_doc else None

    if file_storage:
        # Verify ownership
        if file_storage.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        file_path = Path(file_storage.file_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Determine content type
        content_type = file_storage.content_type
        
        # If encrypted, decrypt
        if file_storage.encrypted:
            # For encrypted files, we'd decrypt here
            # For now, assume files are stored encrypted on disk and need decryption
            # This is a simplified version
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            try:
                decrypted_data = encryption_service.decrypt_bytes(encrypted_data)
                # Return decrypted file as streaming response
                return StreamingResponse(
                    iter([decrypted_data]),
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f'attachment; filename="{file_path.name}"'
                    }
                )
            except Exception as e:
                app_logger.log_error(f"Error decrypting file: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to decrypt file"
                )
        else:
            # Return file directly
            return FileResponse(
                str(file_path),
                media_type=content_type,
                filename=file_path.name
            )
    else:
        # File not in database - might be a generated file (tailored resume)
        # Try to find in uploads directory
        upload_path = Path(settings.storage_local_dir)
        if not upload_path.is_absolute():
            # Make relative to the API directory
            api_dir = Path(__file__).parent.parent.parent  # Go up from routers -> app -> api
            upload_path = api_dir / upload_path
        upload_dir = upload_path.resolve()

        # Check for various file patterns (DOCX, cover letter)
        possible_files = [
            (upload_dir / f"{file_id}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", f"{file_id}.docx"),
            (upload_dir / f"{file_id}_cover_letter.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", f"{file_id}_cover_letter.docx"),
        ]

        # Find the first existing file
        file_path = None
        content_type = None
        filename = None

        for path, mime_type, fname in possible_files:
            if path.exists():
                file_path = path
                content_type = mime_type
                filename = fname
                break

        if not file_path:
            app_logger.log_error(f"No file found for ID: {file_id}. Checked paths: {[str(p[0]) for p, _, _ in possible_files]}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Return file (generated files are not encrypted)
        app_logger.log_info(f"Serving file: {filename} with content-type: {content_type}")
        return FileResponse(
            str(file_path),
            media_type=content_type,
            filename=filename
        )

async def _generate_zip_for_tailoring(resume_file_id: str, cover_file_id: str, upload_dir: Path):
    """Generate a ZIP file with the specific resume and cover letter for a tailoring request"""
    import zipfile
    import io

    # Find the specific files
    resume_path = upload_dir / f"{resume_file_id}.docx"
    cover_path = upload_dir / f"{cover_file_id}_cover_letter.docx" if cover_file_id else None

    app_logger.log_info(f"ZIP generation: resume_path={resume_path} (exists: {resume_path.exists()})")
    app_logger.log_info(f"ZIP generation: cover_path={cover_path} (exists: {cover_path.exists() if cover_path else 'N/A'})")

    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        files_added = 0

        # Create a folder structure in the ZIP
        folder_name = "Job_Application_Package/"

        # Add resume
        if resume_path.exists():
            zip_file.write(str(resume_path), f"{folder_name}Tailored_Resume.docx")
            files_added += 1
            app_logger.log_info(f"Added resume: {resume_path.name} to {folder_name}")
        else:
            app_logger.log_error(f"Resume file not found: {resume_path}")

        # Add cover letter if it exists
        if cover_path and cover_path.exists():
            zip_file.write(str(cover_path), f"{folder_name}Cover_Letter.docx")
            files_added += 1
            app_logger.log_info(f"Added cover letter: {cover_path.name} to {folder_name}")
        elif cover_file_id:
            app_logger.log_error(f"Cover letter file not found: {cover_path}")

        # Add a README file in the folder
        if files_added > 0:
            readme_content = f"""Job Application Package

This package contains your tailored application documents:

{f"• Tailored_Resume.docx - Your customized resume" if resume_path.exists() else ""}
{f"• Cover_Letter.docx - Your personalized cover letter" if cover_path and cover_path.exists() else ""}

Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best of luck with your job application!
"""
            zip_file.writestr(f"{folder_name}README.txt", readme_content)

        if files_added == 0:
            zip_file.writestr("README.txt", "No documents available for download.")
            app_logger.log_warning("No files found for ZIP generation")

    zip_buffer.seek(0)

    # Return the ZIP as streaming response
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="Application_Package.zip"'
        }
    )


async def _generate_fresh_zip_response(file_id: str, upload_dir: Path):
    """Generate a fresh ZIP file with current available documents (fallback method)"""
    import zipfile
    import io

    # Find the 2 most recent DOCX files (should be the resume and cover letter from the current tailoring)
    all_docx_files = [f for f in upload_dir.glob("*.docx") if not "_application_package" in f.name]
    base_files = sorted(all_docx_files, key=lambda f: f.stat().st_mtime, reverse=True)[:2]

    app_logger.log_info(f"ZIP generation: found {len(all_docx_files)} total DOCX files, using {len(base_files)} most recent")

    # Create ZIP in memory with folder structure
    zip_buffer = io.BytesIO()
    folder_name = "Job_Application_Package/"

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        files_added = 0
        for file_path in base_files:
            if file_path.exists():
                # Create a nice filename for the ZIP
                if 'cover_letter' in file_path.name:
                    zip_name = f"{folder_name}Cover_Letter.docx"
                else:
                    zip_name = f"{folder_name}Tailored_Resume.docx"

                zip_file.write(str(file_path), zip_name)
                files_added += 1
                app_logger.log_info(f"Added {file_path.name} as {zip_name} to ZIP")

        if files_added == 0:
            zip_file.writestr("README.txt", "No documents available for download.")
        else:
            # Add a README file in the folder
            readme_content = f"""Job Application Package

This package contains your tailored application documents:

{f"• Tailored_Resume.docx - Your customized resume" if any('cover_letter' not in f.name for f in base_files if f.exists()) else ""}
{f"• Cover_Letter.docx - Your personalized cover letter" if any('cover_letter' in f.name for f in base_files if f.exists()) else ""}

Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best of luck with your job application!
"""
            zip_file.writestr(f"{folder_name}README.txt", readme_content)

        zip_buffer.seek(0)

        # Return the ZIP as streaming response
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="Application_Package.zip"'
            }
        )
