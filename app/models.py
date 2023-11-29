from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.database import Base


class Memory(Base):
    __tablename__ = 'memories'
    #__tablename__ = 'omr'
    id = Column(Integer, primary_key=True, nullable=False, server_default=text('1'))
    user_message = Column(String, nullable=False)
    llm_response = Column(String, nullable=False)
    conversations_summary = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, server_default=text('1'))
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
