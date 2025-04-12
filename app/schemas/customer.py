from typing import Optional, List
from pydantic import BaseModel

# Shared properties
class CustomerBase(BaseModel):
    name: Optional[str] = None
    contact_number: Optional[str] = None

# Properties to receive on customer creation
class CustomerCreate(CustomerBase):
    pass

# Properties to receive on customer update
class CustomerUpdate(CustomerBase):
    pass

# Properties shared by models stored in DB
class CustomerInDBBase(CustomerBase):
    customer_id: int

    class Config:
        from_attributes = True

# Properties to return to client
class Customer(CustomerInDBBase):
    pass

# Properties properties stored in DB
class CustomerInDB(CustomerInDBBase):
    pass