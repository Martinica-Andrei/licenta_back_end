from sqlalchemy import Column, String, Integer
from .base import Base

class BookData(Base):
    __tablename__ = "book_data"

    id = Column(Integer, primary_key=True)
    title = Column(String(1_000), nullable=False)
    description = Column(String(50_000), nullable=True)
    authors = Column(String(5000), nullable=True)
    previewlink = Column(String(2000), nullable=True)
    infolink = Column(String(2000), nullable=True)
    categories = Column(String(2000), nullable=True)