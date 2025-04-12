from typing import Optional, List
from pydantic import BaseModel, Field

# Shared properties
class TableBase(BaseModel):
    table_number: str
    capacity: int = Field(..., ge=1)

# Properties to receive on table creation
class TableCreate(TableBase):
    pass

# Properties to receive on table update
class TableUpdate(TableBase):
    table_number: Optional[str] = None
    capacity: Optional[int] = None

# Properties shared by models stored in DB
class TableInDBBase(TableBase):
    table_id: int

    class Config:
        from_attributes = True

# Properties to return to client
class Table(TableInDBBase):
    pass

# Properties properties stored in DB
class TableInDB(TableInDBBase):
    pass