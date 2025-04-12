from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import order as order_controller
from app.controllers import customer as customer_controller
from app.schemas.order import Order, OrderCreate, OrderUpdate, OrderWithDetails
from app.schemas.waitstaff import Waitstaff

router = APIRouter()

@router.get("/", response_model=List[Order])
def read_orders(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    table_id: Optional[int] = None,
    waiter_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Retrieve orders.
    """
    orders = order_controller.get_orders(
        db, skip=skip, limit=limit, 
        status=status, customer_id=customer_id,
        table_id=table_id, waiter_id=waiter_id
    )
    return orders

@router.post("/", response_model=Order)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Create new order.
    """
    # Set the current user as the waiter if not specified
    if not order_in.waiter_id:
        order_in.waiter_id = current_user.staff_id
        
    # Create the order
    return order_controller.create_order(db, order=order_in)

@router.get("/{order_id}", response_model=OrderWithDetails)
def read_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Get order by ID with all details.
    """
    order = order_controller.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.put("/{order_id}", response_model=Order)
def update_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update an order.
    """
    order = order_controller.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order_controller.update_order(db, order_id=order_id, order=order_in)

@router.delete("/{order_id}", response_model=Order)
def delete_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Delete an order.
    """
    # Only managers can delete orders
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    order = order_controller.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order_controller.delete_order(db, order_id=order_id)

@router.put("/{order_id}/status", response_model=Order)
def update_order_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    status: str,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update the status of an order.
    """
    order = order_controller.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    # Validate status
    valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
        
    return order_controller.update_order_status(db, order_id=order_id, status=status)