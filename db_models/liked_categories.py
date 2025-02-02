from sqlalchemy import Column, Integer, ForeignKey
from db import Base

class LikedCategories(Base):
    __tablename__ = "liked_categories"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer(), ForeignKey('category.id'), nullable=False)
    user_id = Column(Integer(), ForeignKey('user.id'), nullable=False)