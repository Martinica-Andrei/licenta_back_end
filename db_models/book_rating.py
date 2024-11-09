from sqlalchemy import Column, Integer, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base

class BookRating(Base):
    __tablename__ = "book_rating"

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer(), ForeignKey('book.id'), nullable=False)
    user_id = Column(Integer(), ForeignKey('user.id'), nullable=True)
    rating = Column(Enum("Like", "Dislike"), nullable=False)

    user = relationship('User', back_populates='book_ratings')
    book = relationship('Book', back_populates='ratings')

    __table_args__ = (
        UniqueConstraint('book_id', 'user_id', name='unique_book_id_user_id'),
    )
