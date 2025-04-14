from fastapi import APIRouter

from app.routers import menu_item, category, waitstaff, order, order_item, table, customer

api_router = APIRouter()
api_router.include_router(menu_item.router, prefix="/menu-items", tags=["menu-items"])
api_router.include_router(category.router, prefix="/categories", tags=["categories"])
api_router.include_router(waitstaff.router, prefix="/waitstaff", tags=["waitstaff"])
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
api_router.include_router(order_item.router, prefix="/order-items", tags=["order-items"])
api_router.include_router(table.router, prefix="/tables", tags=["tables"])
api_router.include_router(customer.router, prefix="/customers", tags=["customers"])