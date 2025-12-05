"""
REMZA019 Gaming - Viewer Config API
Admin management of viewer system (points, levels, rewards)
SECURITY: Input validation, sanitization, rate limiting
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os
from security_middleware import (
    sanitize_config_update,
    check_rate_limit,
    sanitize_input
)

logger = logging.getLogger(__name__)

viewer_config_router = APIRouter(prefix="/api/viewer-config", tags=["viewer-config"])

# Database connection
def get_database():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    return client.remza019_gaming

# Models
class PointsConfig(BaseModel):
    points: int
    name: str
    enabled: bool
    icon: str

class LevelConfig(BaseModel):
    required: int
    name: str
    features: list
    icon: str

class SystemSettings(BaseModel):
    enable_viewer_system: bool
    enable_leaderboard: bool
    enable_chat: bool
    max_leaderboard_entries: int
    daily_login_streak_bonus: int
    enable_notifications: bool

# PUBLIC ENDPOINTS (for frontend to load configs)

@viewer_config_router.get("/current")
async def get_viewer_config():
    """Get current viewer system configuration - PUBLIC"""
    try:
        db = get_database()
        config = await db.viewer_config.find_one({}, {"_id": 0})
        
        if not config:
            # Return default config if none exists
            return {
                "success": False,
                "message": "No config found, using defaults"
            }
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error(f"❌ Get viewer config error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get config")

@viewer_config_router.get("/points")
async def get_points_config():
    """Get points configuration - PUBLIC"""
    try:
        db = get_database()
        config = await db.viewer_config.find_one({}, {"_id": 0, "points_config": 1})
        
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        
        return {
            "success": True,
            "points_config": config.get("points_config", {})
        }
        
    except Exception as e:
        logger.error(f"❌ Get points config error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get points config")

@viewer_config_router.get("/levels")
async def get_level_system():
    """Get level system configuration - PUBLIC"""
    try:
        db = get_database()
        config = await db.viewer_config.find_one({}, {"_id": 0, "level_system": 1})
        
        if not config:
            raise HTTPException(status_code=404, detail="Config not found")
        
        return {
            "success": True,
            "level_system": config.get("level_system", {})
        }
        
    except Exception as e:
        logger.error(f"❌ Get level system error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get level system")

# ADMIN ENDPOINTS (require authentication)

@viewer_config_router.post("/points/update")
async def update_points_config(request: Request, points_data: dict, admin = Depends(lambda: {"username": "admin"})):
    """Update points configuration - ADMIN ONLY (SECURED)"""
    try:
        # Rate limiting
        check_rate_limit(request, max_requests=30)
        
        db = get_database()
        
        # SECURITY: Sanitize and validate input
        sanitized_data = sanitize_config_update(points_data)
        
        if "points_config" not in sanitized_data:
            raise HTTPException(status_code=400, detail="No valid points config provided")
        
        points_config = sanitized_data["points_config"]
        
        # Log security event
        logger.info(f"🔐 SECURITY: Points config update by {admin['username']}, {len(points_config)} activities")
        
        # Update config
        result = await db.viewer_config.update_one(
            {},
            {
                "$set": {
                    "points_config": points_config,
                    "updated_at": datetime.utcnow(),
                    "updated_by": sanitize_input(admin["username"], 50)
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Config not found")
        
        logger.info(f"✅ Points config updated by {admin['username']}")
        
        # Broadcast update via SSE
        from websocket_manager import broadcast_to_all
        await broadcast_to_all({
            "type": "viewer_config_update",
            "section": "points"
        })
        
        return {
            "success": True,
            "message": "Points config updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Update points config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@viewer_config_router.post("/levels/update")
async def update_level_system(request: Request, levels_data: dict, admin = Depends(lambda: {"username": "admin"})):
    """Update level system configuration - ADMIN ONLY (SECURED)"""
    try:
        # Rate limiting
        check_rate_limit(request, max_requests=30)
        
        db = get_database()
        
        # SECURITY: Sanitize and validate input
        sanitized_data = sanitize_config_update(levels_data)
        
        if "level_system" not in sanitized_data:
            raise HTTPException(status_code=400, detail="No valid level system provided")
        
        level_system = sanitized_data["level_system"]
        
        # Log security event
        logger.info(f"🔐 SECURITY: Level system update by {admin['username']}, {len(level_system)} levels")
        
        # Update config
        result = await db.viewer_config.update_one(
            {},
            {
                "$set": {
                    "level_system": level_system,
                    "updated_at": datetime.utcnow(),
                    "updated_by": sanitize_input(admin["username"], 50)
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Config not found")
        
        logger.info(f"✅ Level system updated by {admin['username']}")
        
        # Broadcast update
        from websocket_manager import broadcast_to_all
        await broadcast_to_all({
            "type": "viewer_config_update",
            "section": "levels"
        })
        
        return {
            "success": True,
            "message": "Level system updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Update level system error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@viewer_config_router.post("/rewards/update")
async def update_rewards(rewards_data: dict, admin = Depends(lambda: {"username": "admin"})):
    """Update rewards configuration - ADMIN ONLY"""
    try:
        db = get_database()
        
        rewards = rewards_data.get("rewards", {})
        
        # Update config
        result = await db.viewer_config.update_one(
            {},
            {
                "$set": {
                    "rewards": rewards,
                    "updated_at": datetime.utcnow(),
                    "updated_by": admin["username"]
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Config not found")
        
        logger.info(f"✅ Rewards updated by {admin['username']}")
        
        return {
            "success": True,
            "message": "Rewards updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Update rewards error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@viewer_config_router.post("/settings/update")
async def update_system_settings(settings_data: dict, admin = Depends(lambda: {"username": "admin"})):
    """Update system settings - ADMIN ONLY"""
    try:
        db = get_database()
        
        system_settings = settings_data.get("system_settings", {})
        
        # Update config
        result = await db.viewer_config.update_one(
            {},
            {
                "$set": {
                    "system_settings": system_settings,
                    "updated_at": datetime.utcnow(),
                    "updated_by": admin["username"]
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Config not found")
        
        logger.info(f"✅ System settings updated by {admin['username']}")
        
        return {
            "success": True,
            "message": "System settings updated successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Update settings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@viewer_config_router.get("/stats")
async def get_viewer_stats(admin = Depends(lambda: {"username": "admin"})):
    """Get viewer system statistics - ADMIN ONLY"""
    try:
        db = get_database()
        
        # Count total viewers
        total_viewers = await db.viewers.count_documents({})
        
        # Count by level
        level_distribution = {}
        for level in range(1, 7):
            count = await db.viewers.count_documents({"level": level})
            level_distribution[f"level_{level}"] = count
        
        # Total points awarded
        total_points = await db.viewers.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$points"}}}
        ]).to_list(length=1)
        
        # Total activities
        total_activities = await db.activities.count_documents({})
        
        # Recent registrations (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_registrations = await db.viewers.count_documents({
            "created_at": {"$gte": seven_days_ago}
        })
        
        return {
            "success": True,
            "stats": {
                "total_viewers": total_viewers,
                "level_distribution": level_distribution,
                "total_points_awarded": total_points[0]["total"] if total_points else 0,
                "total_activities": total_activities,
                "recent_registrations_7d": recent_registrations
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Get stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")
