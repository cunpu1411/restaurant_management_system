from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import payment as payment_controller
from app.controllers import order as order_controller
from app.schemas.payment import Payment, PaymentCreate, PaymentUpdate
from app.schemas.waitstaff import Waitstaff

router = APIRouter()

@router.get("/", response_model=List[Payment])
def read_payments(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Retrieve payments.
    """
    # Only managers can view all payments
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    payments = payment_controller.get_payments(db, skip=skip, limit=limit)
    return payments

@router.get("/by-order/{order_id}", response_model=List[Payment])
def read_payments_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Retrieve payments for a specific order.
    """
    # First check if order exists
    order = order_controller.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    payments = payment_controller.get_payments_by_order(db, order_id=order_id)
    return payments

@router.post("/", response_model=Payment)
def create_payment(
    *,
    db: Session = Depends(get_db),
    payment_in: PaymentCreate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Create new payment.
    """
    # Check if order exists
    order = order_controller.get_order(db, order_id=payment_in.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    # Validate payment method
    valid_methods = ['cash', 'credit_card', 'debit_card', 'mobile_payment']
    if payment_in.payment_method not in valid_methods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment method. Must be one of: {', '.join(valid_methods)}"
        )
        
    # Create the payment
    return payment_controller.create_payment(db, payment=payment_in)

@router.get("/{payment_id}", response_model=Payment)
def read_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Get payment by ID.
    """
    payment = payment_controller.get_payment(db, payment_id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment

@router.put("/{payment_id}", response_model=Payment)
def update_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    payment_in: PaymentUpdate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update a payment.
    """
    # Only managers can update payments
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    payment = payment_controller.get_payment(db, payment_id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
        
    # Validate payment method if provided
    if payment_in.payment_method:
        valid_methods = ['cash', 'credit_card', 'debit_card', 'mobile_payment']
        if payment_in.payment_method not in valid_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payment method. Must be one of: {', '.join(valid_methods)}"
            )
        
    return payment_controller.update_payment(db, payment_id=payment_id, payment=payment_in)

@router.delete("/{payment_id}", response_model=Payment)
def delete_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Delete a payment.
    """
    # Only managers can delete payments
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    payment = payment_controller.get_payment(db, payment_id=payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment_controller.delete_payment(db, payment_id=payment_id)

@router.get("/check-paid/{order_id}")
def check_order_fully_paid(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Check if an order is fully paid.
    """
    # First check if order exists
    order = order_controller.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    is_paid = payment_controller.is_order_fully_paid(db, order_id=order_id)
    total_paid = payment_controller.get_total_payments_for_order(db, order_id=order_id)
    
    return {
        "order_id": order_id,
        "total_amount": float(order.total_amount),
        "total_paid": float(total_paid),
        "is_fully_paid": is_paid
    }