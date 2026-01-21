from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId


class FileStorage(BaseModel):
    """File storage model for MongoDB"""
    id: Optional[str] = None  # Store ObjectId as string in Pydantic model
    user_id: str
    file_path: str  # Path in storage
    encrypted: bool = True
    content_type: str
    size: int
    created_at: datetime = datetime.utcnow()
    
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
