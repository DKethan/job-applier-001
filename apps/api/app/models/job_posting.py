from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class JobPosting(BaseModel):
    """Job posting model for MongoDB"""
    id: Optional[str] = None  # Store ObjectId as string in Pydantic model
    source_url: str
    provider: str
    company_name: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    apply_url: Optional[str] = None
    description_html: Optional[str] = None
    description_text: str
    application_form_schema: Optional[List[Dict[str, Any]]] = None  # Array of ApplicationField dicts
    raw: Dict[str, Any]  # RawExtraction dict
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
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
