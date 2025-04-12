from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.menu_item import MenuItem

# Shared properties
class OrderItemBase(BaseModel):
    order_id: Optional[int] = None
    menu_item_id: int
    quantity: int = Field(1, ge=1)
    special_request: Optional[str] = None
    status: str = "pending"

# Properties to receive on order item creation
class OrderItemCreate(OrderItemBase):
    pass

# Properties to receive on order item update
class OrderItemUpdate(OrderItemBase):
    menu_item_id: Optional[int] = None
    quantity: Optional[int] = None
    special_request: Optional[str] = None
    status: Optional[str] = None

# Properties shared by models stored in DB
class OrderItemInDBBase(OrderItemBase):
    order_item_id: int
    order_id: int

    class Config:
        from_attributes = True

# Properties to return to client
class OrderItem(OrderItemInDBBase):
    pass

# Properties to return to client with menu item details
class OrderItemWithDetails(OrderItem):
    menu_item: Optional[MenuItem] = None

# Properties stored in DB
class OrderItemInDB(OrderItemInDBBase):
    pass