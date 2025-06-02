from sqlalchemy import Column, String, Integer, Text, Index
from sqlalchemy.orm import relationship
from db import Base
from pathlib import Path
import base64
import utils
import numpy as np

class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(1_000), nullable=False)
    description = Column(Text(50_000), nullable=False)
    link = Column(String(2000), nullable=False)
    image_link = Column(String(2000), nullable=True)
    nr_likes = Column(Integer, nullable=False, server_default='0')
    nr_dislikes = Column(Integer, nullable=False, server_default='0')

    authors = relationship('BookAuthors')
    categories = relationship('Category', secondary="book_categories")
    ratings = relationship('BookRating', lazy="noload")

    __table_args__ = (
        Index('ix_fulltext_title', 'title', mysql_prefix='FULLTEXT'),
    )