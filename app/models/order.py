from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Order(Base):
    __tablename__ = "order"
    
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=True)
    table_id = Column(Integer, ForeignKey("table.table_id"), nullable=True)
    waiter_id = Column(Integer, ForeignKey("waitstaff.staff_id"), nullable=True)
    order_date = Column(DateTime, default=func.now(), nullable=False)
    status = Column(Enum('pending', 'processing', 'completed', 'cancelled'), default='pending', nullable=False)
    total_amount = Column(DECIMAL(10, 2), default=0.00)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    table = relationship("Table", back_populates="orders")
    waiter = relationship("Waitstaff", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.order_id}, status={self.status}, total={self.total_amount})>"