from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MemoryBase(BaseModel):
    user_message: str
    llm_response: str
    conversations_summary: str
    published: Optional[bool] = True
    rating: Optional[int] = None


class MemoryCreate(MemoryBase):
    pass


class MemoryResponse(MemoryBase):
    id: Optional[int]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
        #from_orm = True
