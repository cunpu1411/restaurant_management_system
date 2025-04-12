from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

class Category(Base):
    __tablename__ = "category"
    
    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    menu_items = relationship("MenuItem", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.category_id}, name={self.name})>"