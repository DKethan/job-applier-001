from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
import os
import json
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.models.user import User
from app.models.profile import Profile as ProfileModel
from app.models.file_storage import FileStorage
from app.routers.auth import get_current_user
from app.schemas.profile import ProfileSchema, ProfileCreate, ProfileUpdate, ProfileResponse, ProfileStatus, ProfileCompleteness, Basics
from app.services.resume_parser import resume_parser
from app.utils.encryption import encryption_service
from app.config import settings
from app.utils.app_logger import app_logger
from datetime import datetime

router = APIRouter()


@router.get("/me", response_model=ProfileStatus)
async def get_profile_status(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Get user's profile status and completeness"""
    # Check if user has a profile
    profile_doc = db.profiles.find_one({"user_id": str(current_user.id)})

    if not profile_doc:
        return ProfileStatus(hasProfile=False)

    # Decrypt and parse profile
    profile_model = ProfileModel.from_dict(profile_doc)
    decrypted_json = encryption_service.decrypt(profile_model.encrypted_json)
    profile_data = json.loads(decrypted_json)

    # Calculate completeness
    profile = ProfileSchema(**profile_data)
    completeness = ProfileCompleteness(
        education=len(profile.education) > 0,
        experience=len(profile.work_experience) > 0,
        skills=len(profile.skills) > 0,
        projects=len(profile.projects) > 0,
        publications=bool((profile.certifications and len(profile.certifications) > 0) or
                         (profile.awards and len(profile.awards) > 0))
    )

    return ProfileStatus(
        hasProfile=True,
        profileId=str(profile_model.id),
        profileCompleteness=completeness,
        profile=profile
    )


@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    profile: ProfileSchema,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Update user's profile"""

    # Check if profile exists
    profile_doc = db.profiles.find_one({"user_id": str(current_user.id)})
    if not profile_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Encrypt the updated profile
    import json
    profile_json = json.dumps(profile.model_dump())
    encrypted_json = encryption_service.encrypt(profile_json)

    # Update profile
    update_data = {
        "encrypted_json": encrypted_json,
        "updated_at": datetime.utcnow()
    }

    db.profiles.update_one(
        {"user_id": str(current_user.id)},
        {"$set": update_data}
    )

    # Return updated profile
    updated_doc = db.profiles.find_one({"user_id": str(current_user.id)})
    profile_model = ProfileModel.from_dict(updated_doc)
    return ProfileResponse(
        id=str(profile_model.id),
        user_id=profile_model.user_id,
        profile=profile,
        created_at=profile_model.created_at,
        updated_at=profile_model.updated_at
    )


def ensure_upload_dir():
    """Ensure upload directory exists"""
    # Convert to absolute path (handles relative paths like ./data/uploads)
    upload_path = Path(settings.storage_local_dir)
    if not upload_path.is_absolute():
        # Make relative to the API directory
        api_dir = Path(__file__).parent.parent.parent  # Go up from routers -> app -> api
        upload_path = api_dir / upload_path
    upload_dir = upload_path.resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


@router.post("/resume/upload", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Upload and parse resume"""
    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: PDF, DOCX, DOC"
        )

    # Save file
    upload_dir = ensure_upload_dir()
    import uuid
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix if file.filename else ".pdf"
    file_path = upload_dir / f"{file_id}{file_ext}"

    try:
        # Write file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract text
        resume_text = resume_parser.extract_text(str(file_path), file.content_type)

        # Parse with LLM
        profile_data = resume_parser.parse_with_llm(resume_text)

        # Encrypt profile JSON
        profile_json = json.dumps(profile_data.model_dump())
        encrypted_profile = encryption_service.encrypt(profile_json)

        # Check if user already has a profile
        existing_profile = db.profiles.find_one({"user_id": str(current_user.id)})
        existing_file_storage = None
        if existing_profile:
            # Get existing file storage to clean it up later
            existing_file_storage = db.file_storage.find_one({"user_id": str(current_user.id)})

        # Store new file record
        file_storage = FileStorage(
            user_id=str(current_user.id),
            file_path=str(file_path),
            encrypted=True,
            content_type=file.content_type,
            size=len(content)
        )

        if existing_profile:
            # Update existing profile
            db.profiles.update_one(
                {"user_id": str(current_user.id)},
                {"$set": {
                    "encrypted_json": encrypted_profile,
                    "updated_at": datetime.utcnow()
                }}
            )
            # Update file storage
            db.file_storage.update_one(
                {"user_id": str(current_user.id)},
                {"$set": file_storage.to_dict()}
            )

            # Clean up old file if it exists
            if existing_file_storage and existing_file_storage.get("file_path"):
                old_file_path = Path(existing_file_storage["file_path"])
                if old_file_path.exists():
                    old_file_path.unlink()

            profile_id = existing_profile["_id"]
        else:
            # Create new profile
            db.file_storage.insert_one(file_storage.to_dict())

            profile = ProfileModel(
                user_id=str(current_user.id),
                encrypted_json=encrypted_profile
            )
            result = db.profiles.insert_one(profile.to_dict())
            profile_id = result.inserted_id

        # Return profile (decrypted for response)
        profile_doc = db.profiles.find_one({"_id": profile_id})
        profile = ProfileModel.from_dict(profile_doc)

        return ProfileResponse(
            id=str(profile.id),
            user_id=str(current_user.id),
            profile=profile_data,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )

    except Exception as e:
        app_logger.log_error(f"Error processing resume: {e}")
        # Cleanup file if exists
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Get profile by ID"""
    try:
        profile_doc = db.profiles.find_one({
            "_id": ObjectId(profile_id),
            "user_id": str(current_user.id)
        })
    except Exception:
        profile_doc = None

    if not profile_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    profile = ProfileModel.from_dict(profile_doc)

    # Decrypt and return
    decrypted_json = encryption_service.decrypt(profile.encrypted_json)
    profile_data = ProfileSchema(**json.loads(decrypted_json))

    return ProfileResponse(
        id=str(profile.id),
        user_id=profile.user_id,
        profile=profile_data,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Update profile"""
    try:
        profile_doc = db.profiles.find_one({
            "_id": ObjectId(profile_id),
            "user_id": str(current_user.id)
        })
    except Exception:
        profile_doc = None

    if not profile_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    profile = ProfileModel.from_dict(profile_doc)

    # Encrypt updated profile
    profile_json = json.dumps(profile_update.profile.model_dump())
    encrypted_profile = encryption_service.encrypt(profile_json)

    # Update
    db.profiles.update_one(
        {"_id": ObjectId(profile_id)},
        {"$set": {
            "encrypted_json": encrypted_profile,
            "updated_at": datetime.utcnow()
        }}
    )

    # Return decrypted
    return ProfileResponse(
        id=str(profile.id),
        user_id=profile.user_id,
        profile=profile_update.profile,
        created_at=profile.created_at,
        updated_at=datetime.utcnow()
    )


@router.get("/", response_model=list[ProfileResponse])
async def list_profiles(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """List all profiles for current user"""
    profile_docs = db.profiles.find({"user_id": str(current_user.id)})

    result = []
    for profile_doc in profile_docs:
        profile = ProfileModel.from_dict(profile_doc)
        decrypted_json = encryption_service.decrypt(profile.encrypted_json)
        profile_data = ProfileSchema(**json.loads(decrypted_json))
        result.append(ProfileResponse(
            id=str(profile.id),
            user_id=profile.user_id,
            profile=profile_data,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        ))

    return result
