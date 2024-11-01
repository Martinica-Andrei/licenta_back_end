from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class LikedBook(Base):
    __tablename__ = "liked_book"

    id = Column(Integer, primary_key=True, autoincrement=False)
    book_id = Column(Integer(), ForeignKey('book.id'), nullable=False)
    user_id = Column(Integer(), ForeignKey('user.id'), nullable=False)

    user = relationship('User', back_populates='liked_books')
