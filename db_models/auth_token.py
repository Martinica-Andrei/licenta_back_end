from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db import Base

class AuthToken(Base):
    __tablename__ = "auth_token"

    id = Column(Integer, primary_key=True)
    token = Column(String(64), nullable=False, unique=True)
    creation_date = Column(DateTime(), nullable=False)
    expiration_date = Column(DateTime(), nullable=False)

    user_id = Column(Integer(), ForeignKey('user.id'), nullable=False)

    user = relationship('User')