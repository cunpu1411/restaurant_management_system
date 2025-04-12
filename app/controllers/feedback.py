from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate

def get_feedback(db: Session, feedback_id: int) -> Optional[Feedback]:
    return db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()

def get_feedbacks_by_order(db: Session, order_id: int) -> List[Feedback]:
    return db.query(Feedback).filter(Feedback.order_id == order_id).all()

def get_feedbacks_by_customer(db: Session, customer_id: int) -> List[Feedback]:
    return db.query(Feedback).filter(Feedback.customer_id == customer_id).all()

def get_feedbacks(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Feedback]:
    return db.query(Feedback).order_by(Feedback.feedback_date.desc()).offset(skip).limit(limit).all()

def create_feedback(db: Session, feedback: FeedbackCreate) -> Feedback:
    db_feedback = Feedback(
        customer_id=feedback.customer_id,
        order_id=feedback.order_id,
        rating=feedback.rating,
        comment=feedback.comment,
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def update_feedback(
    db: Session, feedback_id: int, feedback: FeedbackUpdate
) -> Optional[Feedback]:
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback:
        update_data = feedback.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_feedback, field, value)
        db.commit()
        db.refresh(db_feedback)
    return db_feedback

def delete_feedback(db: Session, feedback_id: int) -> Optional[Feedback]:
    db_feedback = get_feedback(db, feedback_id)
    if db_feedback:
        db.delete(db_feedback)
        db.commit()
        return db_feedback
    return None

def get_average_rating(db: Session) -> float:
    """Get the average rating of all feedbacks"""
    avg_rating = db.query(func.avg(Feedback.rating)).scalar()
    return float(avg_rating) if avg_rating else 0.0

def get_rating_statistics(db: Session) -> Dict[str, Any]:
    """Get statistics about ratings"""
    total = db.query(Feedback).count()
    ratings = {}
    
    for i in range(1, 6):  # Ratings from 1 to 5
        ratings[i] = db.query(Feedback).filter(Feedback.rating == i).count()
        
    return {
        "total": total,
        "average": get_average_rating(db),
        "ratings": ratings
    }