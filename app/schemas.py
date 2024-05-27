from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class MemoryBase(BaseModel):
    user_message: str
    llm_response: str
    conversations_summary: str


class MemoryCreate(MemoryBase):
    pass


class UserOut(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: int
    email: EmailStr
    created_at: Optional[datetime] = None
        

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
    model_config = ConfigDict(extra='allow')

    writing_text: str
        

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
    model_config = ConfigDict(extra='allow')

    post_id: int
    dir: int = Field(..., ge=0, le=1)
