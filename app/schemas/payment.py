from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

# Shared properties
class PaymentBase(BaseModel):
    order_id: int
    amount: Decimal = Field(..., ge=0)
    payment_method: str

# Properties to receive on payment creation
class PaymentCreate(PaymentBase):
    pass

# Properties to receive on payment update
class PaymentUpdate(PaymentBase):
    amount: Optional[Decimal] = None
    payment_method: Optional[str] = None

# Properties shared by models stored in DB
class PaymentInDBBase(PaymentBase):
    payment_id: int
    payment_date: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class Payment(PaymentInDBBase):
    pass

# Properties stored in DB
class PaymentInDB(PaymentInDBBase):
    pass