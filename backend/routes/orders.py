"""
Order management routes for placing new orders and viewing order history.
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from ..models import Order
from ..database import orders_collection

# Split so the read replica / write replica of the deployment can each mount only
# the half it serves. The monolith (main.py) mounts both.
read_router = APIRouter(prefix="/orders", tags=["Orders"])
write_router = APIRouter(prefix="/orders", tags=["Orders"])

@write_router.post("")
def place_order(order: Order):
    """
    Place a new order for a user.
    """
    order_data = order.model_dump()
    order_data["created_at"] = datetime.now(timezone.utc).isoformat()
    orders_collection.insert_one(order_data)
    return {"message": "Order placed successfully"}


@read_router.get("/{user_email}")
def get_order_history(user_email: str):
    """
    Get a user's past orders, most recent first.
    """
    orders = list(
        orders_collection.find({"user_email": user_email}, {"_id": 0}).sort("created_at", -1)
    )
    return orders

