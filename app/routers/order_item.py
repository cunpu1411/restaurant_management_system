from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import order_item as order_item_controller
from app.controllers import order as order_controller
from app.schemas.order_item import OrderItem, OrderItemCreate, OrderItemUpdate
from app.schemas.order import OrderUpdate
from app.schemas.waitstaff import Waitstaff

router = APIRouter()

@router.get("/by-order/{order_id}", response_model=List[OrderItem])
def read_order_items_by_order(
    order_id: int,
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Retrieve order items by order.
    """
    # First check if order exists
    order = order_controller.get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    items = order_item_controller.get_order_items_by_order(
        db, order_id=order_id, skip=skip, limit=limit
    )
    return items

@router.post("/", response_model=OrderItem)
def create_order_item(
    *,
    db: Session = Depends(get_db),
    order_item_in: OrderItemCreate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Add item to an order.
    """
    # Check if order exists
    order = order_controller.get_order(db, order_id=order_item_in.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
        
    # Create the order item
    order_item = order_item_controller.create_order_item(db, order_item=order_item_in)
    
    # Recalculate order total
    order_controller.update_order(
        db, 
        order_id=order_item_in.order_id, 
        order=OrderUpdate(
            total_amount=order_controller.calculate_order_total(db, order_item_in.order_id)
        )
    )
    
    return order_item

@router.get("/{order_item_id}", response_model=OrderItem)
def read_order_item(
    *,
    db: Session = Depends(get_db),
    order_item_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Get order item by ID.
    """
    order_item = order_item_controller.get_order_item(db, order_item_id=order_item_id)
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    return order_item

@router.put("/{order_item_id}", response_model=OrderItem)
def update_order_item(
    *,
    db: Session = Depends(get_db),
    order_item_id: int,
    order_item_in: OrderItemUpdate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update an order item.
    """
    order_item = order_item_controller.get_order_item(db, order_item_id=order_item_id)
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
        
    updated_item = order_item_controller.update_order_item(
        db, order_item_id=order_item_id, order_item=order_item_in
    )
    
    # Recalculate order total if quantity changed
    if "quantity" in order_item_in.dict(exclude_unset=True):
        order_controller.update_order(
            db, 
            order_id=order_item.order_id, 
            order=OrderUpdate(
                total_amount=order_controller.calculate_order_total(db, order_item.order_id)
            )
        )
    
    return updated_item

@router.delete("/{order_item_id}", response_model=OrderItem)
def delete_order_item(
    *,
    db: Session = Depends(get_db),
    order_item_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Delete an order item.
    """
    order_item = order_item_controller.get_order_item(db, order_item_id=order_item_id)
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
        
    order_id = order_item.order_id
    deleted_item = order_item_controller.delete_order_item(db, order_item_id=order_item_id)
    
    # Recalculate order total
    order_controller.update_order(
        db, 
        order_id=order_id, 
        order=OrderUpdate(
            total_amount=order_controller.calculate_order_total(db, order_id)
        )
    )
    
    return deleted_item

@router.put("/{order_item_id}/status", response_model=OrderItem)
def update_order_item_status(
    *,
    db: Session = Depends(get_db),
    order_item_id: int,
    status: str,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update the status of an order item.
    """
    order_item = order_item_controller.get_order_item(db, order_item_id=order_item_id)
    if not order_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
        
    # Validate status
    valid_statuses = ['pending', 'preparing', 'ready', 'delivered', 'cancelled']
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
        
    return order_item_controller.update_order_item_status(db, order_item_id=order_item_id, status=status)