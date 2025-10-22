from fastapi import APIRouter
from controllers.orderController import (
    get_order_by_id_controller,
    get_top_products_by_category_controller
)

router = APIRouter(prefix="/orders")

# Route 1 — Get Top 5 most purchased products by category (aggregation)
# IMPORTANT: This must come BEFORE the {order_id} route to avoid conflicts
# Example: GET /orders/top-products
@router.get("/top-products")
async def get_top_products_by_category():
    """
    Get top 5 most frequently purchased products in the last month, grouped by category
    """
    return get_top_products_by_category_controller()

# Route 2 — Get single order by ID
# Example: GET /orders/{order_id}
@router.get("/{order_id}")
async def get_order_by_id(order_id: str):
    """
    Get a single order by its ID with populated user and product details
    """
    return get_order_by_id_controller(order_id)
