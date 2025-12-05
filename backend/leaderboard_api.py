"""
019 Solutions - Leaderboard System
Track and display top viewers by points
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger("leaderboard")

leaderboard_router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

# Pydantic models
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    username: str
    points: int
    level: int
    badge: Optional[str] = None

class UpdatePointsRequest(BaseModel):
    user_id: str
    username: str
    points: int
    level: int

def get_database():
    from server import get_database as get_db
    return get_db()

@leaderboard_router.get("/top")
async def get_top_viewers(limit: int = 10):
    """Get top viewers by points - PUBLIC"""
    try:
        db = get_database()
        
        # Get top viewers from database sorted by points
        viewers = await db.viewers.find(
            {},
            {"_id": 0, "user_id": 1, "username": 1, "points": 1, "level": 1}
        ).sort("points", -1).limit(limit).to_list(length=limit)
        
        # Assign ranks and badges
        leaderboard = []
        for idx, viewer in enumerate(viewers):
            rank = idx + 1
            badge = None
            
            # Assign badges for top 3
            if rank == 1:
                badge = "🥇 Champion"
            elif rank == 2:
                badge = "🥈 Runner-up"
            elif rank == 3:
                badge = "🥉 Top 3"
            
            leaderboard.append(LeaderboardEntry(
                rank=rank,
                user_id=viewer.get("user_id", ""),
                username=viewer.get("username", "Unknown"),
                points=viewer.get("points", 0),
                level=viewer.get("level", 1),
                badge=badge
            ))
        
        return {"leaderboard": [entry.dict() for entry in leaderboard]}
        
    except Exception as e:
        logger.error(f"❌ Get top viewers error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@leaderboard_router.get("/user/{user_id}")
async def get_user_rank(user_id: str):
    """Get a specific user's rank and position - PUBLIC"""
    try:
        db = get_database()
        
        # Get user
        user = await db.viewers.find_one(
            {"user_id": user_id},
            {"_id": 0, "user_id": 1, "username": 1, "points": 1, "level": 1}
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Count users with more points to determine rank
        users_ahead = await db.viewers.count_documents(
            {"points": {"$gt": user.get("points", 0)}}
        )
        
        rank = users_ahead + 1
        badge = None
        
        if rank == 1:
            badge = "🥇 Champion"
        elif rank == 2:
            badge = "🥈 Runner-up"
        elif rank == 3:
            badge = "🥉 Top 3"
        elif rank <= 10:
            badge = "⭐ Top 10"
        
        return {
            "rank": rank,
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "points": user.get("points", 0),
            "level": user.get("level", 1),
            "badge": badge
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get user rank error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user rank")

@leaderboard_router.post("/update")
async def update_leaderboard(request: UpdatePointsRequest):
    """Update viewer points in leaderboard - PUBLIC"""
    try:
        db = get_database()
        
        # Update or insert viewer
        await db.viewers.update_one(
            {"user_id": request.user_id},
            {
                "$set": {
                    "username": request.username,
                    "points": request.points,
                    "level": request.level,
                    "last_updated": datetime.now().isoformat()
                }
            },
            upsert=True
        )
        
        # Get updated rank
        users_ahead = await db.viewers.count_documents(
            {"points": {"$gt": request.points}}
        )
        rank = users_ahead + 1
        
        logger.info(f"✅ Leaderboard updated: {request.username} - {request.points} pts (Rank #{rank})")
        
        return {
            "success": True,
            "rank": rank,
            "points": request.points
        }
        
    except Exception as e:
        logger.error(f"❌ Update leaderboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update leaderboard")

@leaderboard_router.get("/stats")
async def get_leaderboard_stats():
    """Get overall leaderboard statistics - PUBLIC"""
    try:
        db = get_database()
        
        # Get statistics
        total_viewers = await db.viewers.count_documents({})
        
        # Get top viewer
        top_viewer = await db.viewers.find(
            {},
            {"_id": 0, "username": 1, "points": 1}
        ).sort("points", -1).limit(1).to_list(length=1)
        top_viewer = top_viewer[0] if top_viewer else None
        
        # Calculate average points
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_points": {"$avg": "$points"},
                    "total_points": {"$sum": "$points"}
                }
            }
        ]
        
        stats = await db.viewers.aggregate(pipeline).to_list(length=1)
        avg_points = stats[0].get("avg_points", 0) if stats else 0
        total_points = stats[0].get("total_points", 0) if stats else 0
        
        return {
            "total_viewers": total_viewers,
            "total_points": total_points,
            "average_points": round(avg_points, 1),
            "top_viewer": top_viewer.get("username") if top_viewer else None,
            "top_points": top_viewer.get("points") if top_viewer else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Get leaderboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard stats")
