"""Business data constants for the fake shop."""

from typing import Any

CART_ITEMS = [
    {
        "id": "item-notebook",
        "name": "Notebook",
        "price": 12.00,
        "quantity": 2,
        "total": 24.00,
    },
    {
        "id": "item-pens",
        "name": "Pen set",
        "price": 8.50,
        "quantity": 1,
        "total": 8.50,
    },
]

SUBTOTAL: float = 32.50
SHIPPING_COST: float = 4.00
TOTAL: float = 36.50
ORDER_ID: str = "QA-1042"
SUCCESS_TEXT: str = "Order confirmed"
WRONG_TOTAL: float = 32.50


def get_cart_data() -> dict[str, Any]:
    """Return cart items and calculated pricing summary."""
    return {
        "items": CART_ITEMS,
        "cart_items": CART_ITEMS,
        "subtotal": f"{SUBTOTAL:.2f}",
        "shipping": f"{SHIPPING_COST:.2f}",
        "total": f"{TOTAL:.2f}",
        "order_id": ORDER_ID,
        "success_text": SUCCESS_TEXT,
    }
