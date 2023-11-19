from sqlalchemy import Column, INTEGER, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class Memory(Base):
    __tablename__ = 'memories'
    id = Column(INTEGER, primary_key=True, nullable=False)
    user_message = Column(String, nullable=False)
    llm_response = Column(String, nullable=False)
    conversations_summary = Column(String, nullable=False)
    # published = Column(Boolean, default=True)
    # rating = INTEGER()
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
