from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# Shared properties
class WaitstaffBase(BaseModel):
    name: str
    role: str
    contact_number: Optional[str] = None
    username: str

# Properties to receive on waitstaff creation
class WaitstaffCreate(WaitstaffBase):
    password: str = Field(..., min_length=6)

# Properties to receive on waitstaff update
class WaitstaffUpdate(WaitstaffBase):
    name: Optional[str] = None
    role: Optional[str] = None
    contact_number: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

# Properties shared by models stored in DB
class WaitstaffInDBBase(WaitstaffBase):
    staff_id: int

    class Config:
        from_attributes = True

# Properties to return to client
class Waitstaff(WaitstaffInDBBase):
    pass

# Properties properties stored in DB
class WaitstaffInDB(WaitstaffInDBBase):
    password_hash: str

# For token authentication
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

# For login
class Login(BaseModel):
    username: str
    password: str