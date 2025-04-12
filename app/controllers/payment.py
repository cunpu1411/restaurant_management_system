from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.controllers import order as order_controller

def get_payment(db: Session, payment_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.payment_id == payment_id).first()

def get_payments_by_order(db: Session, order_id: int) -> List[Payment]:
    return db.query(Payment).filter(Payment.order_id == order_id).all()

def get_payments(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Payment]:
    return db.query(Payment).order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()

def create_payment(db: Session, payment: PaymentCreate) -> Payment:
    db_payment = Payment(
        order_id=payment.order_id,
        amount=payment.amount,
        payment_method=payment.payment_method,
    )
    db.add(db_payment)
    
    # Update order status to completed if payment is made
    order = order_controller.get_order(db, payment.order_id)
    if order and order.status != 'completed':
        order.status = 'completed'
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update_payment(
    db: Session, payment_id: int, payment: PaymentUpdate
) -> Optional[Payment]:
    db_payment = get_payment(db, payment_id)
    if db_payment:
        update_data = payment.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment, field, value)
        db.commit()
        db.refresh(db_payment)
    return db_payment

def delete_payment(db: Session, payment_id: int) -> Optional[Payment]:
    db_payment = get_payment(db, payment_id)
    if db_payment:
        db.delete(db_payment)
        db.commit()
        return db_payment
    return None

def get_total_payments_for_order(db: Session, order_id: int) -> Decimal:
    """Calculate the total amount paid for an order"""
    payments = get_payments_by_order(db, order_id)
    return sum(payment.amount for payment in payments)

def is_order_fully_paid(db: Session, order_id: int) -> bool:
    """Check if an order is fully paid"""
    order = order_controller.get_order(db, order_id)
    if not order:
        return False
        
    total_paid = get_total_payments_for_order(db, order_id)
    return total_paid >= order.total_amount