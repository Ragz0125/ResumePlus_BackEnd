from sqlalchemy import Column, Integer, String
from databases.sql_db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,unique=True, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    hashed_password = Column(String)
    email = Column(String, unique=True, nullable=False)