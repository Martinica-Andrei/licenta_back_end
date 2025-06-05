from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from db import Base

class LikedCategories(Base):
    __tablename__ = "liked_categories"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer(), ForeignKey('category.id'), nullable=False)
    user_id = Column(Integer(), ForeignKey('user.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('category_id', 'user_id', name='unique_category_id_user_id'),
    )