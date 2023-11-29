from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class MemoryBase(BaseModel):
    user_message: str
    llm_response: str
    conversations_summary: str
    # published: Optional[bool] = True
    rating: Optional[int] = None


class MemoryCreate(MemoryBase):
    pass


class MemoryResponse(MemoryBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
