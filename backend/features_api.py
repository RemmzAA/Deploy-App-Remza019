from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models
class Feature(BaseModel):
    icon: str
    title: str
    description: str
    tooltip: str
    order: int = 0
    enabled: bool = True

class FeatureInDB(Feature):
    id: str
    created_at: str
    updated_at: str

class FeatureCreate(Feature):
    pass

class FeatureUpdate(BaseModel):
    icon: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tooltip: Optional[str] = None
    order: Optional[int] = None
    enabled: Optional[bool] = None

# Dependency to get database
async def get_database() -> AsyncIOMotorDatabase:
    from server import db
    return db

# Public endpoint - Get all enabled features
@router.get("/api/features", response_model=List[FeatureInDB])
async def get_features(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Get all enabled features ordered by order field"""
    try:
        features = await db.features.find(
            {"enabled": True},
            {"_id": 0}
        ).sort("order", 1).to_list(100)
        
        logger.info(f"Retrieved {len(features)} features")
        return features
    except Exception as e:
        logger.error(f"Error fetching features: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch features")

# Admin endpoint - Get all features (including disabled)
@router.get("/api/admin/features", response_model=List[FeatureInDB])
async def admin_get_all_features(db: AsyncIOMotorDatabase = Depends(get_database)):
    """Admin: Get all features"""
    try:
        features = await db.features.find({}, {"_id": 0}).sort("order", 1).to_list(100)
        logger.info(f"Admin retrieved {len(features)} features")
        return features
    except Exception as e:
        logger.error(f"Error fetching all features: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch features")

# Admin endpoint - Create feature
@router.post("/api/admin/features", response_model=FeatureInDB)
async def admin_create_feature(
    feature: FeatureCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Admin: Create a new feature"""
    try:
        feature_id = str(ObjectId())
        now = datetime.utcnow().isoformat()
        
        feature_doc = {
            "id": feature_id,
            **feature.dict(),
            "created_at": now,
            "updated_at": now
        }
        
        await db.features.insert_one(feature_doc)
        logger.info(f"Created feature: {feature_id}")
        
        # Return without _id
        feature_doc.pop("_id", None)
        return FeatureInDB(**feature_doc)
    except Exception as e:
        logger.error(f"Error creating feature: {e}")
        raise HTTPException(status_code=500, detail="Failed to create feature")

# Admin endpoint - Update feature
@router.put("/api/admin/features/{feature_id}", response_model=FeatureInDB)
async def admin_update_feature(
    feature_id: str,
    feature_update: FeatureUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Admin: Update a feature"""
    try:
        # Build update document
        update_data = {k: v for k, v in feature_update.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await db.features.update_one(
            {"id": feature_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Feature not found")
        
        # Fetch updated feature
        updated_feature = await db.features.find_one({"id": feature_id}, {"_id": 0})
        logger.info(f"Updated feature: {feature_id}")
        
        return FeatureInDB(**updated_feature)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feature: {e}")
        raise HTTPException(status_code=500, detail="Failed to update feature")

# Admin endpoint - Delete feature
@router.delete("/api/admin/features/{feature_id}")
async def admin_delete_feature(
    feature_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Admin: Delete a feature"""
    try:
        result = await db.features.delete_one({"id": feature_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Feature not found")
        
        logger.info(f"Deleted feature: {feature_id}")
        return {"message": "Feature deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feature: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete feature")

# Admin endpoint - Reorder features
@router.post("/api/admin/features/reorder")
async def admin_reorder_features(
    feature_ids: List[str],
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Admin: Reorder features by providing ordered list of IDs"""
    try:
        # Update order for each feature
        for index, feature_id in enumerate(feature_ids):
            await db.features.update_one(
                {"id": feature_id},
                {"$set": {"order": index, "updated_at": datetime.utcnow().isoformat()}}
            )
        
        logger.info(f"Reordered {len(feature_ids)} features")
        return {"message": "Features reordered successfully"}
    except Exception as e:
        logger.error(f"Error reordering features: {e}")
        raise HTTPException(status_code=500, detail="Failed to reorder features")

# Initialize default features if collection is empty
async def initialize_default_features(db: AsyncIOMotorDatabase):
    """Initialize default features if none exist"""
    try:
        count = await db.features.count_documents({})
        
        if count == 0:
            logger.info("Initializing default features...")
            
            default_features = [
                {
                    "id": str(ObjectId()),
                    "icon": "📺",
                    "title": "GLEDAJ I ZARAĐUJ",
                    "description": "Zarađuj poene gledanjem strimova",
                    "tooltip": "Earn 5 points for every 10 minutes of stream watching. Build your points by being an active viewer!",
                    "order": 0,
                    "enabled": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(ObjectId()),
                    "icon": "💬",
                    "title": "UŽIVO CHAT",
                    "description": "Ćaskaj sa drugima g ledaocima",
                    "tooltip": "Participate in live chat and earn 2 points per message. Connect with other viewers in real-time!",
                    "order": 1,
                    "enabled": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(ObjectId()),
                    "icon": "🗳️",
                    "title": "GLASAJ I PREDVIĐI",
                    "description": "Učestvuj u anketama",
                    "tooltip": "Vote in live polls and make predictions. Earn 3 points for each poll participation!",
                    "order": 2,
                    "enabled": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(ObjectId()),
                    "icon": "⭐",
                    "title": "VIP PRISTUP",
                    "description": "Otkljucaj ekskluzivne funkcije",
                    "tooltip": "Reach Level 4 to unlock VIP features: private chat, custom emotes, and priority support!",
                    "order": 3,
                    "enabled": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(ObjectId()),
                    "icon": "🏆",
                    "title": "SISTEM NIVOA",
                    "description": "Postani Gaming Legenda",
                    "tooltip": "Progress through 6 levels: Rookie Viewer → Active Watcher → Engaged Fan → VIP Member → Elite Supporter → Gaming Legend!",
                    "order": 4,
                    "enabled": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(ObjectId()),
                    "icon": "🎯",
                    "title": "NAGRADE",
                    "description": "Dobij specijalne pogodnosti i bedževe",
                    "tooltip": "Get special perks and badges as you level up. Unlock moderator access at Level 6!",
                    "order": 5,
                    "enabled": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
            
            await db.features.insert_many(default_features)
            logger.info(f"Initialized {len(default_features)} default features")
    except Exception as e:
        logger.error(f"Error initializing default features: {e}")
