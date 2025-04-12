from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

class Waitstaff(Base):
    __tablename__ = "waitstaff"
    
    staff_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    contact_number = Column(String(20), nullable=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Relationships
    orders = relationship("Order", back_populates="waiter")
    
    def __repr__(self):
        return f"<Waitstaff(id={self.staff_id}, name={self.name}, role={self.role})>"