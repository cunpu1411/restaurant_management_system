from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

from app.schemas.category import Category

# Shared properties
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    is_available: bool = True
    category_id: int

# Properties to receive on menu item creation
class MenuItemCreate(MenuItemBase):
    pass

# Properties to receive on menu item update
class MenuItemUpdate(MenuItemBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_available: Optional[bool] = None
    category_id: Optional[int] = None

# Properties shared by models stored in DB
class MenuItemInDBBase(MenuItemBase):
    menu_item_id: int

    class Config:
        from_attributes = True

# Properties to return to client
class MenuItem(MenuItemInDBBase):
    pass

# Properties to return to client with category info
class MenuItemWithCategory(MenuItem):
    category: Optional[Category] = None

# Properties properties stored in DB
class MenuItemInDB(MenuItemInDBBase):
    pass