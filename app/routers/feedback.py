from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import feedback as feedback_controller
from app.controllers import order as order_controller
from app.schemas.feedback import Feedback, FeedbackCreate, FeedbackUpdate
from app.schemas.waitstaff import Waitstaff

router = APIRouter()

@router.get("/", response_model=List[Feedback])
def read_feedbacks(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Retrieve feedbacks.
    """
    # Only managers can view all feedbacks
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    feedbacks = feedback_controller.get_feedbacks(db, skip=skip, limit=limit)
    return feedbacks

@router.get("/statistics")
def get_feedback_statistics(
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Get feedback statistics.
    """
    stats = feedback_controller.get_rating_statistics(db)
    return stats

@router.get("/by-order/{order_id}", response_model=List[Feedback])
def read_feedbacks_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Retrieve feedbacks for a specific order.
    """
    # First check if order exists
    order = order_controller.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    feedbacks = feedback_controller.get_feedbacks_by_order(db, order_id=order_id)
    return feedbacks

@router.post("/", response_model=Feedback)
def create_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_in: FeedbackCreate
) -> Any:
    """
    Create new feedback. No authentication required for customers to leave feedback.
    """
    # Check if order exists
    order = order_controller.get_order(db, order_id=feedback_in.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    # Validate rating (should be handled by schema, but double check)
    if feedback_in.rating < 1 or feedback_in.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
        
    # Create the feedback
    return feedback_controller.create_feedback(db, feedback=feedback_in)

@router.get("/{feedback_id}", response_model=Feedback)
def read_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Get feedback by ID.
    """
    feedback = feedback_controller.get_feedback(db, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback

@router.put("/{feedback_id}", response_model=Feedback)
def update_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    feedback_in: FeedbackUpdate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update a feedback. Only managers can update feedback.
    """
    # Only managers can update feedback
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    feedback = feedback_controller.get_feedback(db, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
        
    # Validate rating if provided
    if feedback_in.rating is not None and (feedback_in.rating < 1 or feedback_in.rating > 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
        
    return feedback_controller.update_feedback(db, feedback_id=feedback_id, feedback=feedback_in)

@router.delete("/{feedback_id}", response_model=Feedback)
def delete_feedback(
    *,
    db: Session = Depends(get_db),
    feedback_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Delete a feedback. Only managers can delete feedback.
    """
    # Only managers can delete feedback
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    feedback = feedback_controller.get_feedback(db, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback_controller.delete_feedback(db, feedback_id=feedback_id)