from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

class Table(Base):
    __tablename__ = "table"
    
    table_id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String(20), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String(20), default="available") 
    
    # Relationships
    orders = relationship("Order", back_populates="table")
    
    def __repr__(self):
        return f"<Table(id={self.table_id}, number={self.table_number}, capacity={self.capacity})>"