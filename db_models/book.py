from sqlalchemy import Column, String, Integer, Text, Index
from sqlalchemy.orm import relationship
from db import Base
from pathlib import Path
import base64
import utils


class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(1_000), nullable=False)
    description = Column(Text(50_000), nullable=False)
    link = Column(String(2000), nullable=False)
    image_link = Column(String(2000), nullable=True)

    authors = relationship('BookAuthors', back_populates='book')
    categories = relationship('BookCategories', back_populates='book')
    ratings = relationship('BookRating', back_populates='book')

    __table_args__ = (
        Index('ix_fulltext_title', 'title', mysql_prefix='FULLTEXT'),
    )

    @staticmethod
    def get_image_base64(filename):
        if filename is None:
            return None
        filepath: Path = utils.BOOKS_DATA_IMAGES / filename
        if filepath.is_file():
            with open(filepath, 'rb') as file:
                binary_data = file.read()
                base64_bytes = base64.b64encode(binary_data)
                base64_str = base64_bytes.decode('utf-8')
                return base64_str
        else:
            return None

    def image_base64(self):
        return Book.get_image_base64(self.image_link)