from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.table import Table
from app.schemas.table import TableCreate, TableUpdate

def get_table(db: Session, table_id: int) -> Optional[Table]:
    return db.query(Table).filter(Table.table_id == table_id).first()

def get_table_by_number(db: Session, table_number: str) -> Optional[Table]:
    return db.query(Table).filter(Table.table_number == table_number).first()

def get_tables(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Table]:
    return db.query(Table).offset(skip).limit(limit).all()

def create_table(db: Session, table: TableCreate) -> Table:
    db_table = Table(
        table_number=table.table_number,
        capacity=table.capacity,
    )
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

def update_table(
    db: Session, table_id: int, table: TableUpdate
) -> Optional[Table]:
    db_table = get_table(db, table_id)
    if db_table:
        update_data = table.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_table, field, value)
        db.commit()
        db.refresh(db_table)
    return db_table

def delete_table(db: Session, table_id: int) -> Optional[Table]:
    db_table = get_table(db, table_id)
    if db_table:
        db.delete(db_table)
        db.commit()
        return db_table
    return None