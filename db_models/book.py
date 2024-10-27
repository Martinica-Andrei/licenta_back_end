from sqlalchemy import Column, String, Integer, Text, Index
from sqlalchemy.orm import relationship
from db import Base

class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(1_000), nullable=False)
    description = Column(Text(50_000), nullable=False)
    link = Column(String(2000), nullable=False)
    image_link = Column(String(2000), nullable=True)

    authors = relationship('BookAuthors', back_populates='book')
    categories = relationship('BookCategories', back_populates='book')

    __table_args__ = (
        Index('ix_fulltext_title', 'title', mysql_prefix='FULLTEXT'),
    )
