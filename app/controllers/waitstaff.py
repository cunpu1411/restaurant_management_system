from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.waitstaff import Waitstaff
from app.schemas.waitstaff import WaitstaffCreate, WaitstaffUpdate
from app.core.security import get_password_hash, verify_password

def get_waitstaff(db: Session, staff_id: int) -> Optional[Waitstaff]:
    return db.query(Waitstaff).filter(Waitstaff.staff_id == staff_id).first()

def get_waitstaff_by_username(db: Session, username: str) -> Optional[Waitstaff]:
    return db.query(Waitstaff).filter(Waitstaff.username == username).first()

def get_waitstaffs(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Waitstaff]:
    return db.query(Waitstaff).offset(skip).limit(limit).all()

def create_waitstaff(db: Session, waitstaff: WaitstaffCreate) -> Waitstaff:
    hashed_password = get_password_hash(waitstaff.password)
    db_waitstaff = Waitstaff(
        name=waitstaff.name,
        role=waitstaff.role,
        contact_number=waitstaff.contact_number,
        username=waitstaff.username,
        password_hash=hashed_password,
    )
    db.add(db_waitstaff)
    db.commit()
    db.refresh(db_waitstaff)
    return db_waitstaff

def update_waitstaff(
    db: Session, staff_id: int, waitstaff: WaitstaffUpdate
) -> Optional[Waitstaff]:
    db_waitstaff = get_waitstaff(db, staff_id)
    if db_waitstaff:
        update_data = waitstaff.dict(exclude_unset=True, exclude={"password"})
        for field, value in update_data.items():
            setattr(db_waitstaff, field, value)
        
        # Update password if provided
        if waitstaff.password:
            db_waitstaff.password_hash = get_password_hash(waitstaff.password)
            
        db.commit()
        db.refresh(db_waitstaff)
    return db_waitstaff

def delete_waitstaff(db: Session, staff_id: int) -> Optional[Waitstaff]:
    db_waitstaff = get_waitstaff(db, staff_id)
    if db_waitstaff:
        db.delete(db_waitstaff)
        db.commit()
        return db_waitstaff
    return None

def authenticate_waitstaff(db: Session, username: str, password: str) -> Optional[Waitstaff]:
    waitstaff = get_waitstaff_by_username(db, username)
    if not waitstaff:
        print(f"User {username} not found in database")
        return None
    
    print(f"User found, checking password")
    
    if not verify_password(password, waitstaff.password_hash):
        print(f"Password verification failed for {username}")
        return None
    
    print(f"Authentication successful for {username}")
    return waitstaff