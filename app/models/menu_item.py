from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DECIMAL
from sqlalchemy.orm import relationship

from app.core.database import Base

class MenuItem(Base):
    __tablename__ = "menu_item"
    
    menu_item_id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("category.category_id"))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)
    
    # Relationships
    category = relationship("Category", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")
    
    def __repr__(self):
        return f"<MenuItem(id={self.menu_item_id}, name={self.name}, price={self.price})>"