from sqlalchemy import Column, String
from db import Base

#only purpose of this table is to remove all stopwords from fulltext search
class NoStopWord(Base):
    __tablename__ = "no_stop_word"

    value = Column(String(1), nullable=False, primary_key=True, autoincrement=False)