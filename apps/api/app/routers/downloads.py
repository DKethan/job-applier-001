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

router = APIRouter()


@router.get("/{file_id}")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Download a file (verify ownership, decrypt if needed)"""
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
        
        # Check for PDF first, then DOCX
        pdf_path = upload_dir / f"{file_id}.pdf"
        docx_path = upload_dir / f"{file_id}.docx"
        
        # If PDF exists, serve it
        if pdf_path.exists():
            file_path = pdf_path
            content_type = "application/pdf"
            filename = pdf_path.name
        # If PDF doesn't exist but DOCX does, serve DOCX (fallback for missing PDF)
        elif docx_path.exists():
            app_logger.log_info(f"PDF {file_id}.pdf not found, serving DOCX instead")
            file_path = docx_path
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = docx_path.name
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Return file (generated files are not encrypted)
        return FileResponse(
            str(file_path),
            media_type=content_type,
            filename=filename
        )
