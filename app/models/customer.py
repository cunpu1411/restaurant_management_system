from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

class Customer(Base):
    __tablename__ = "customer"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    contact_number = Column(String(20), nullable=True)
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    feedbacks = relationship("Feedback", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(id={self.customer_id}, name={self.name})>"