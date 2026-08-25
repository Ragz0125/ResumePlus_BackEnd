from sqlalchemy import Boolean, Integer, String, Column, ForeignKey

from databases.sql_db import Base

class Conversations(Base):
    __tablename__ = "conversations"
    
    id = Column(String, unique=True, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"), nullable=False, index=True)
    hil_activity_status = Column(Boolean, default=False, nullable=False)