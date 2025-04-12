from fastapi import APIRouter

from app.routers import (
    category,
    menu_item,
    customer,
    waitstaff,
    table,
    order,
    order_item,
    payment,
    feedback,
    auth,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(category.router, prefix="/categories", tags=["Categories"])
api_router.include_router(menu_item.router, prefix="/menu-items", tags=["Menu Items"])
api_router.include_router(customer.router, prefix="/customers", tags=["Customers"])
api_router.include_router(waitstaff.router, prefix="/waitstaff", tags=["Waitstaff"])
api_router.include_router(table.router, prefix="/tables", tags=["Tables"])
api_router.include_router(order.router, prefix="/orders", tags=["Orders"])
api_router.include_router(order_item.router, prefix="/order-items", tags=["Order Items"])
api_router.include_router(payment.router, prefix="/payments", tags=["Payments"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])