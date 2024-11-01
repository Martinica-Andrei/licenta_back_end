from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db import Base

class BookRating(Base):
    __tablename__ = "book_rating"

    id = Column(Integer, primary_key=True, autoincrement=False)
    book_id = Column(Integer(), ForeignKey('book.id'), nullable=False)
    user_id = Column(Integer(), ForeignKey('user.id'), nullable=False)
    rating = Column(Enum("Like", "Dislike"), nullable=False)

    user = relationship('User', back_populates='book_ratings')
