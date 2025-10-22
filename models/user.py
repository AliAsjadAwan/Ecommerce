from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    name: str
    email: EmailStr
    location: Optional[str] = None
    totalSpent: Optional[float] = 0.0
    purchaseCount: Optional[int] = 0
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserInDB(User):
    id: Optional[str] = Field(alias="_id")
