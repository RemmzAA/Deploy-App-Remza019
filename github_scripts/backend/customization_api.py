"""
REMZA019 Gaming - Customization API
Stores site customization (colors, logo, links) in database
Real-time updates via SSE broadcast
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import Optional
import logging
from datetime import datetime

from admin_api import get_current_admin

logger = logging.getLogger("customization_api")

customization_router = APIRouter(prefix="/customization", tags=["customization"])

class CustomizationData(BaseModel):
    userName: str = "REMZA019 Gaming"
    matrixColor: str = "#00ff00"
    textColor: str = "#00ff00"
    logoUrl: str = "/remza-logo.png"
    youtubeChannelId: Optional[str] = ""
    discordLink: Optional[str] = ""
    twitterLink: Optional[str] = ""
    instagramLink: Optional[str] = ""
    twitchLink: Optional[str] = ""
    tiktokLink: Optional[str] = ""

def get_database():
    """Get database instance"""
    from server import get_database as get_db
    return get_db()

async def broadcast_customization_update(data: dict):
    """Broadcast customization update to all connected clients via SSE"""
    try:
        from admin_api import broadcast_admin_update
        await broadcast_admin_update("customization_update", data)
        logger.info("✅ Customization update broadcasted to all clients")
    except Exception as e:
        logger.error(f"Failed to broadcast customization update: {e}")

@customization_router.get("/current")
async def get_customization():
    """Get current site customization (PUBLIC - no auth required)"""
    try:
        db = get_database()
        
        # Get from database
        customization = await db.customization.find_one(
            {"type": "site_config"},
            {"_id": 0}
        )
        
        if not customization:
            # Return defaults if not found
            default_data = CustomizationData().dict()
            logger.info("📝 Returning default customization")
            return {"success": True, "data": default_data}
        
        # Remove type field
        customization.pop("type", None)
        customization.pop("updated_at", None)
        
        logger.info("✅ Customization retrieved from database")
        return {"success": True, "data": customization}
        
    except Exception as e:
        logger.error(f"❌ Get customization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@customization_router.post("/save")
async def save_customization(
    data: CustomizationData,
    admin = Depends(get_current_admin)
):
    """Save site customization (ADMIN ONLY)"""
    try:
        db = get_database()
        
        # Prepare data for database
        customization_data = data.dict()
        customization_data["type"] = "site_config"
        customization_data["updated_at"] = datetime.now()
        customization_data["updated_by"] = admin.get("username", "admin")
        
        # Upsert to database
        result = await db.customization.update_one(
            {"type": "site_config"},
            {"$set": customization_data},
            upsert=True
        )
        
        logger.info(f"✅ Customization saved by {admin.get('username')}")
        
        # Broadcast update to all clients
        await broadcast_customization_update(data.dict())
        
        return {
            "success": True,
            "message": "Customization saved successfully!",
            "data": data.dict()
        }
        
    except Exception as e:
        logger.error(f"❌ Save customization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@customization_router.post("/reset")
async def reset_customization(admin = Depends(get_current_admin)):
    """Reset to default customization (ADMIN ONLY)"""
    try:
        db = get_database()
        
        # Default data
        default_data = CustomizationData()
        customization_data = default_data.dict()
        customization_data["type"] = "site_config"
        customization_data["updated_at"] = datetime.now()
        customization_data["updated_by"] = admin.get("username", "admin")
        
        # Update database
        await db.customization.update_one(
            {"type": "site_config"},
            {"$set": customization_data},
            upsert=True
        )
        
        logger.info(f"✅ Customization reset to defaults by {admin.get('username')}")
        
        # Broadcast update
        await broadcast_customization_update(default_data.dict())
        
        return {
            "success": True,
            "message": "Customization reset to defaults!",
            "data": default_data.dict()
        }
        
    except Exception as e:
        logger.error(f"❌ Reset customization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
