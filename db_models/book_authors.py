from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base

class BookAuthors(Base):
    __tablename__ = "book_authors"

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer(), ForeignKey('author.id'), nullable=False)
    book_id = Column(Integer(), ForeignKey('book.id'), nullable=False)
    role = Column(String(500), nullable=True)

    author = relationship('Author')

    __table_args__ = (
        UniqueConstraint('book_id', 'author_id', name='unique_book_id_author_id'),
    )