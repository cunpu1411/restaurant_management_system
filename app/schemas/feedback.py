from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Shared properties
class FeedbackBase(BaseModel):
    customer_id: Optional[int] = None
    order_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

# Properties to receive on feedback creation
class FeedbackCreate(FeedbackBase):
    pass

# Properties to receive on feedback update
class FeedbackUpdate(FeedbackBase):
    rating: Optional[int] = None
    comment: Optional[str] = None

# Properties shared by models stored in DB
class FeedbackInDBBase(FeedbackBase):
    feedback_id: int
    feedback_date: datetime

    class Config:
        from_attributes = True

# Properties to return to client
class Feedback(FeedbackInDBBase):
    pass

# Properties stored in DB
class FeedbackInDB(FeedbackInDBBase):
    pass