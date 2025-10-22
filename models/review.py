from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Review(BaseModel):
    user: str  # ObjectId as string
    product: str  # ObjectId as string
    rating: int = Field(..., ge=1, le=5)  # Between 1 and 5
    text: Optional[str] = None
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ReviewInDB(Review):
    id: Optional[str] = Field(alias="_id")
