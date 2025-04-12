from sqlalchemy import Column, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base

class OrderItem(Base):
    __tablename__ = "order_item"
    
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.order_id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_item.menu_item_id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    special_request = Column(Text, nullable=True)
    status = Column(Enum('pending', 'preparing', 'ready', 'delivered', 'cancelled'), default='pending', nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.order_item_id}, order_id={self.order_id}, item_id={self.menu_item_id}, qty={self.quantity})>"