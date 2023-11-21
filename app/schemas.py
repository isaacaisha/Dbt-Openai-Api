from pydantic import BaseModel, EmailStr, conint
from typing import Optional
from datetime import datetime


class MemoryBase(BaseModel):
    user_message: str
    llm_response: str
    conversations_summary: str


class MemoryCreate(MemoryBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MemoryResponse(MemoryBase):
    user_message: str
    llm_response: Optional[str] = None
    conversations_summary: Optional[str] = None
    conversation_id: Optional[int] = None
    owner: Optional[UserOut] = None
    likes: int = 0 


class MemoryUpdate(MemoryBase):
    owner_id: Optional[int] = None


class TextAreaForm(BaseModel):
    writing_text: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    dir: conint(ge=0, le=1) # type: ignore

    class Config:
        from_attributes = True
        #from_orm = True
