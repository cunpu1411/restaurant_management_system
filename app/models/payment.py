from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Payment(Base):
    __tablename__ = "payment"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.order_id"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum('cash', 'credit_card', 'debit_card', 'mobile_payment'), nullable=False)
    payment_date = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.payment_id}, order_id={self.order_id}, amount={self.amount}, method={self.payment_method})>"