from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, distinct
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu_item import MenuItem
from app.models.table import Table
from app.models.waitstaff import Waitstaff
from app.models.payment import Payment

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        # Tổng số đơn hàng
        total_orders = db.query(func.count(Order.order_id)).scalar() or 0
        
        # Tổng doanh thu
        total_revenue = db.query(func.sum(Order.total_amount)).scalar() or 0
        
        # Giá trị trung bình của đơn hàng
        avg_order_value = 0
        if total_orders > 0:
            avg_order_value = total_revenue / total_orders
        
        # Số bàn đang hoạt động (có đơn hàng đang pending hoặc processing)
        active_tables = db.query(func.count(distinct(Order.table_id))).filter(
            Order.status.in_(["pending", "processing"])
        ).scalar() or 0
        
        # Tổng số bàn
        total_tables = db.query(func.count(Table.table_id)).scalar() or 0
        
        # Các đơn hàng gần đây nhất
        recent_orders = db.query(Order).order_by(Order.order_date.desc()).limit(5).all()
        
        # Format đơn hàng để trả về
        formatted_orders = []
        for order in recent_orders:
            items_count = db.query(func.count(OrderItem.order_item_id)).filter(
                OrderItem.order_id == order.order_id
            ).scalar() or 0
            
            formatted_orders.append({
                "order_id": order.order_id,
                "table_number": order.table.table_number if order.table else "N/A",
                "table_id": order.table.table_id if order.table else None,
                "items_count": items_count,
                "total_amount": float(order.total_amount),
                "status": order.status,
                "order_time": order.order_date.isoformat()
            })
        
        # Các món ăn phổ biến nhất
        popular_items = db.query(
            MenuItem.menu_item_id,
            MenuItem.name,
            func.count(OrderItem.order_item_id).label('count')
        ).join(
            OrderItem, MenuItem.menu_item_id == OrderItem.menu_item_id
        ).group_by(
            MenuItem.menu_item_id
        ).order_by(
            func.count(OrderItem.order_item_id).desc()
        ).limit(5).all()
        
        formatted_popular_items = [
            {"id": item[0], "name": item[1], "count": item[2]} 
            for item in popular_items
        ]
        
        # Staff performance (số đơn hàng đã phục vụ)
        staff_performance = db.query(
            Waitstaff.staff_id,
            Waitstaff.name,
            func.count(Order.order_id).label('order_count')
        ).outerjoin(
            Order, Waitstaff.staff_id == Order.waiter_id
        ).group_by(
            Waitstaff.staff_id
        ).all()
        
        # Tính % performance dựa trên số đơn hàng
        max_orders = max([staff[2] for staff in staff_performance]) if staff_performance else 0
        
        formatted_staff = []
        for staff in staff_performance:
            performance = int((staff[2] / max_orders * 100) if max_orders > 0 else 0)
            formatted_staff.append({
                "id": staff[0],
                "name": staff[1],
                "performance": performance
            })
        
        # Sắp xếp theo performance giảm dần
        formatted_staff.sort(key=lambda x: x["performance"], reverse=True)
        
        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "avg_order_value": float(avg_order_value),
            "active_tables": active_tables,
            "total_tables": total_tables,
            "recent_orders": formatted_orders,
            "popular_items": formatted_popular_items,
            "staff_performance": formatted_staff[:5]  # Chỉ lấy top 5
        }
    except Exception as e:
        print(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard statistics: {str(e)}"
        )