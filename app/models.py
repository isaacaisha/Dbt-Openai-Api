from pydantic import BaseModel
from sqlalchemy import Column, INTEGER, String, Boolean, Integer
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


# Pydantic model for request validation
class MemoryCreate(BaseModel):
    user_message: str
    conversations_summary: str


class Memory(Base):
    __tablename__ = 'omr'
    id = Column(INTEGER, primary_key=True, nullable=False)
    user_message = Column(String, nullable=False)
    llm_response = Column(String, nullable=False)
    conversations_summary = Column(String, nullable=False)
    published = Column(Boolean, default=True)
    rating = Integer()
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
