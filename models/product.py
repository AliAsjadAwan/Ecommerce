from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Product(BaseModel):
    name: str
    description: str
    category: str
    brand: str
    price: float
    stock: int
    rating: Optional[float] = 0.0
    ratingCount: Optional[int] = 0
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProductInDB(Product):
    id: Optional[str] = Field(alias="_id")

