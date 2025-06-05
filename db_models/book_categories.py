from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base

class BookCategories(Base):
    __tablename__ = "book_categories"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer(), ForeignKey('category.id'), nullable=False)
    book_id = Column(Integer(), ForeignKey('book.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('category_id', 'book_id', name='category_id_book_id'),
    )