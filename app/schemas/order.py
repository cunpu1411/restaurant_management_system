from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.schemas.order_item import OrderItem, OrderItemCreate
from app.schemas.customer import Customer
from app.schemas.table import Table
from app.schemas.waitstaff import Waitstaff

# Shared properties
class OrderBase(BaseModel):
    customer_id: Optional[int] = None
    table_id: Optional[int] = None
    waiter_id: Optional[int] = None
    status: str = "pending"

# Properties to receive on order creation
class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate] = []

# Properties to receive on order update
class OrderUpdate(OrderBase):
    status: Optional[str] = None
    total_amount: Optional[Decimal] = None

# Properties shared by models stored in DB
class OrderInDBBase(OrderBase):
    order_id: int
    order_date: datetime
    total_amount: Decimal = 0.0

    class Config:
        from_attributes = True

# Properties to return to client
class Order(OrderInDBBase):
    pass

# Properties to return to client with relationships
class OrderWithDetails(Order):
    order_items: List[OrderItem] = []
    customer: Optional[Customer] = None
    table: Optional[Table] = None
    waiter: Optional[Waitstaff] = None

# Properties stored in DB
class OrderInDB(OrderInDBBase):
    pass