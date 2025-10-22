from fastapi import APIRouter
from controllers.userController import get_user_orders_controller

router = APIRouter(prefix="/users")

# Route — Get user orders
# Example: GET /users/{user_id}/orders
@router.get("/{user_id}/orders")
async def get_user_orders(user_id: str):
    """
    Get all orders for a specific user
    """
    return get_user_orders_controller(user_id)
