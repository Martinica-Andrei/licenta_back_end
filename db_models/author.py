from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(500), nullable=False)