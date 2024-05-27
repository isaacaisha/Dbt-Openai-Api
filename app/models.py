from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, joinedload
from datetime import datetime, timezone

from app.database import Base


class Memory(Base):
    __tablename__ = 'api_memories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_message = Column(String, nullable=False)
    llm_response = Column(String, nullable=False)
    conversations_summary = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    owner_id = Column(Integer, ForeignKey('api_users.id', ondelete='CASCADE'), nullable=False)
    
    owner = relationship('User', back_populates='memories')
    votes = relationship("Vote", back_populates="memory", foreign_keys="[Vote.memory_id]")

    def __str__(self):
        return f"Memory(id={self.id}, user_message='{self.user_message}', llm_response='{self.llm_response}')"
    

class User(Base):
    __tablename__ = 'api_users'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    memories = relationship('Memory', back_populates='owner')


class Vote(Base):
    __tablename__ = 'api_votes'
    user_id = Column(Integer, ForeignKey("api_users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("api_memories.id", ondelete="CASCADE"), primary_key=True)

    memory_id = Column(Integer, ForeignKey('api_memories.id'))
    memory = relationship("Memory", back_populates="votes", foreign_keys="[Vote.memory_id]")
