from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId


class User(BaseModel):
    """User model for MongoDB"""
    id: Optional[str] = None  # Store ObjectId as string in Pydantic model
    email: EmailStr
    username: str
    display_name: str
    hashed_password: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
    
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
