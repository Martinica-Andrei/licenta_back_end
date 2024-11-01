from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, and_
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime, timedelta
import secrets
from db import db
from sqlalchemy.exc import IntegrityError
import hashlib

class AuthToken(Base):
    __tablename__ = "auth_token"

    id = Column(Integer, primary_key=True)
    token = Column(String(64), nullable=False, unique=True)
    creation_date = Column(DateTime(), nullable=False)
    expiration_date = Column(DateTime(), nullable=False)

    user_id = Column(Integer(), ForeignKey('user.id'), nullable=False)

    user = relationship('User')

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode('utf-8')).hexdigest()

    @staticmethod
    def authenticate(days_till_expiration, user_id):
        creation_date = datetime.now()
        expiration_date = creation_date + timedelta(days=days_till_expiration)
        while True:
            token = secrets.token_hex(32)
            token_hashed = AuthToken.hash_token(token)
            auth_token = AuthToken(token=token_hashed,
                                    creation_date=creation_date,
                                    expiration_date=expiration_date,
                                    user_id = user_id)
            try:
                db.session.add(auth_token)
                db.session.commit()
                return token
            except IntegrityError as ex:
                db.session.rollback()

    def is_expired(self):
        return (datetime.now() >= self.expiration_date)
    
    @staticmethod
    def remove_expired_tokens_from_user(user_id):
        db.session.query(AuthToken).filter(and_(AuthToken.user_id == user_id, datetime.now() >= AuthToken.expiration_date)).delete()
        db.session.commit()