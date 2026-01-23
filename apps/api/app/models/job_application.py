from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class JobApplication(BaseModel):
    """Job application model for storing application metadata"""
    id: Optional[str] = None
    user_id: str
    job_id: str  # Reference to the job posting
    job_title: str
    company_name: str
    job_url: str
    applied_date: datetime = datetime.utcnow()
    status: str = "draft"  # draft, applied, rejected, accepted
    notes: Optional[str] = None
    # Store tailoring metadata but not the actual files
    tailoring_summary: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

    def to_dict(self) -> dict:
        """Convert to dict for MongoDB"""
        data = self.model_dump(exclude={"id"})
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Create from MongoDB document"""
        if "_id" in data:
            data["id"] = str(data["_id"])
        data.pop("_id", None)
        return cls(**data)