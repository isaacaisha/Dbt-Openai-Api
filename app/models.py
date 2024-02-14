from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, joinedload
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime

from app.database import Base


class Memory(Base):
    __tablename__ = 'api_memories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_message = Column(String, nullable=False)
    llm_response = Column(String, nullable=False)
    conversations_summary = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey('api_users.id', ondelete='CASCADE'), nullable=False)
    
    owner = relationship('User', back_populates='memories')

    def __str__(self):
        return f"Memory(id={self.id}, user_message='{self.user_message}', llm_response='{self.llm_response}')"


class User(Base):
    __tablename__ = 'api_users'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    memories = relationship('Memory', back_populates='owner')


class Vote(Base):
    __tablename__ = 'api_votes'
    user_id = Column(Integer, ForeignKey("api_users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("api_memories.id", ondelete="CASCADE"), primary_key=True)
