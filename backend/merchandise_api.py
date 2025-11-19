"""
REMZA019 Gaming - Merchandise Store Integration
Printful/Teespring print-on-demand merch store
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

merch_router = APIRouter(prefix="/api/merch", tags=["merchandise"])

def get_database():
    from server import get_database as get_db
    return get_db()

class Product(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    image_url: str
    sizes: List[str]
    colors: List[str]
    category: str  # "tshirt", "hoodie", "mug", "poster"

@merch_router.get("/products")
async def get_products(category: Optional[str] = None):
    """Get all merchandise products"""
    try:
        db = get_database()
        
        filter_query = {}
        if category:
            filter_query["category"] = category
        
        products = await db.merchandise.find(filter_query).to_list(length=100)
        
        return {
            "products": products,
            "count": len(products)
        }
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@merch_router.post("/order")
async def create_order(user_id: str, product_id: str, size: str, color: str, quantity: int):
    """Create a merchandise order"""
    try:
        db = get_database()
        
        product = await db.merchandise.find_one({"product_id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Calculate total
        total = product["price"] * quantity
        
        # Create order (integrate with Printful API in production)
        order = {
            "order_id": f"ORD-{datetime.now().timestamp()}",
            "user_id": user_id,
            "product_id": product_id,
            "size": size,
            "color": color,
            "quantity": quantity,
            "total": total,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        await db.orders.insert_one(order)
        
        return {
            "success": True,
            "order_id": order["order_id"],
            "total": total,
            "message": "Order created! Proceed to payment."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))
