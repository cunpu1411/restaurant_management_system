from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import menu_item as menu_item_controller
from app.schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.schemas.waitstaff import Waitstaff

router = APIRouter()

@router.get("/", response_model=List[MenuItem])
def read_menu_items(
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    available_only: bool = False,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve menu items.
    """
    if available_only:
        menu_items = menu_item_controller.get_available_menu_items(
            db, skip=skip, limit=limit, category_id=category_id
        )
    else:
        menu_items = menu_item_controller.get_menu_items(
            db, skip=skip, limit=limit, category_id=category_id
        )
    return menu_items

@router.post("/", response_model=MenuItem)
def create_menu_item(
    *,
    db: Session = Depends(get_db),
    menu_item_in: MenuItemCreate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Create new menu item.
    """
    # Only managers can create menu items
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    return menu_item_controller.create_menu_item(db, menu_item=menu_item_in)

@router.get("/{menu_item_id}", response_model=MenuItem)
def read_menu_item(
    *,
    db: Session = Depends(get_db),
    menu_item_id: int
) -> Any:
    """
    Get menu item by ID.
    """
    menu_item = menu_item_controller.get_menu_item(db, menu_item_id=menu_item_id)
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return menu_item

@router.put("/{menu_item_id}", response_model=MenuItem)
def update_menu_item(
    *,
    db: Session = Depends(get_db),
    menu_item_id: int,
    menu_item_in: MenuItemUpdate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update a menu item.
    """
    # Only managers can update menu items
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    menu_item = menu_item_controller.get_menu_item(db, menu_item_id=menu_item_id)
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return menu_item_controller.update_menu_item(db, menu_item_id=menu_item_id, menu_item=menu_item_in)

@router.delete("/{menu_item_id}", response_model=MenuItem)
def delete_menu_item(
    *,
    db: Session = Depends(get_db),
    menu_item_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Delete a menu item.
    """
    # Only managers can delete menu items
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    menu_item = menu_item_controller.get_menu_item(db, menu_item_id=menu_item_id)
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return menu_item_controller.delete_menu_item(db, menu_item_id=menu_item_id)

@router.put("/{menu_item_id}/toggle-availability", response_model=MenuItem)
def toggle_menu_item_availability(
    *,
    db: Session = Depends(get_db),
    menu_item_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Toggle the availability of a menu item.
    """
    # Waiters and managers can toggle availability
    menu_item = menu_item_controller.get_menu_item(db, menu_item_id=menu_item_id)
    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return menu_item_controller.toggle_availability(db, menu_item_id=menu_item_id)