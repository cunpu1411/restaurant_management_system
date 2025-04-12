from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    
    feedback_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=True)
    order_id = Column(Integer, ForeignKey("order.order_id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    feedback_date = Column(DateTime, default=func.now(), nullable=False)
    
    # Add a check constraint to ensure rating is between 1 and 5
    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='check_rating_range'),
    )
    
    # Relationships
    customer = relationship("Customer", back_populates="feedbacks")
    order = relationship("Order", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<Feedback(id={self.feedback_id}, order_id={self.order_id}, rating={self.rating})>"