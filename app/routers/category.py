from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.controllers import category as category_controller
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.schemas.waitstaff import Waitstaff

router = APIRouter()

@router.get("/", response_model=List[Category])
def read_categories(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve categories.
    """
    categories = category_controller.get_categories(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=Category)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Create new category.
    """
    # Only managers can create categories
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    category = category_controller.get_category_by_name(db, name=category_in.name)
    if category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    return category_controller.create_category(db, category=category_in)

@router.get("/{category_id}", response_model=Category)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: int
) -> Any:
    """
    Get category by ID.
    """
    category = category_controller.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.put("/{category_id}", response_model=Category)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Update a category.
    """
    # Only managers can update categories
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    category = category_controller.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category_controller.update_category(db, category_id=category_id, category=category_in)

@router.delete("/{category_id}", response_model=Category)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user: Waitstaff = Depends(get_current_user)
) -> Any:
    """
    Delete a category.
    """
    # Only managers can delete categories
    if current_user.role != "Manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    category = category_controller.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category_controller.delete_category(db, category_id=category_id)