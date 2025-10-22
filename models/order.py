from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    product: str  # ObjectId as string
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: int = 1

class Order(BaseModel):
    user: str  # ObjectId as string
    items: List[OrderItem]
    totalCost: Optional[float] = None
    status: str = 'placed'
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class OrderInDB(Order):
    id: Optional[str] = Field(alias="_id")