"""
Shopping cart routes: add an item, list a user's items, clear the cart.
"""


from fastapi import APIRouter
from ..models import CartItem
from ..database import cart_collection


# Split so the read replica / write replica of the deployment can each mount only
# the half it serves. The monolith (main.py) mounts both.
read_router = APIRouter(prefix="/cart", tags=["Cart"])
write_router = APIRouter(prefix="/cart", tags=["Cart"])


@write_router.post("/add")
def add_to_cart(item: CartItem):
    """
    Add an item to the user's shopping cart. If the same product is already in
    the cart, its quantity is increased instead of adding a duplicate row.
    """
    existing = cart_collection.find_one(
        {"user_email": item.user_email, "product_name": item.product_name}
    )
    if existing:
        cart_collection.update_one(
            {"_id": existing["_id"]}, {"$inc": {"quantity": item.quantity}}
        )
    else:
        cart_collection.insert_one(item.model_dump())
    return {"message": "Item added to cart"}


@read_router.get("/{user_email}")
def get_cart(user_email: str):
    """
    Get all shopping cart items for a specific user.
    """
    items = list(cart_collection.find({"user_email": user_email}, {"_id": 0}))
    return items


@write_router.delete("/{user_email}")
def clear_cart(user_email: str):
    """
    Clear all shopping cart items for a specific user after checkout.
    """
    cart_collection.delete_many({"user_email": user_email})
    return {"message": "Cart cleared successfully"}