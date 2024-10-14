from sqlalchemy import Column, String, Integer, Text, Index
from db import Base, db

class Book(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String(1_000), nullable=False)
    description = Column(Text(50_000), nullable=True)
    authors = Column(String(5000), nullable=True)
    previewlink = Column(String(2000), nullable=True)
    infolink = Column(String(2000), nullable=True)
    categories = Column(String(2000), nullable=True)

    __table_args__ = (
        Index('ix_fulltext_title', 'title', mysql_prefix='FULLTEXT'),
    )

    def to_dict(self):
        return {k : v for k, v in self.__dict__.items() if k.startswith('_') == False}