"""
REMZA019 Gaming - Viewer Analytics Dashboard
Personal stats, watch time, achievements
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

analytics_router = APIRouter(prefix="/api/analytics", tags=["analytics"])

def get_database():
    from server import get_database as get_db
    return get_db()

@analytics_router.get("/user/{user_id}")
async def get_user_analytics(user_id: str):
    """Get comprehensive user analytics"""
    try:
        db = get_database()
        
        viewer = await db.viewers.find_one({"user_id": user_id})
        if not viewer:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get activity history
        activities = await db.activities.find({
            "user_id": user_id
        }).sort("timestamp", -1).limit(100).to_list(length=100)
        
        # Calculate stats
        total_points = viewer.get("points", 0)
        level = viewer.get("level", 1)
        
        # Points earned over time (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_activities = [a for a in activities if a.get("timestamp", datetime.min) >= thirty_days_ago]
        
        daily_points = {}
        for activity in recent_activities:
            day = activity["timestamp"].strftime("%Y-%m-%d")
            daily_points[day] = daily_points.get(day, 0) + activity.get("points", 0)
        
        # Activity breakdown
        activity_breakdown = {}
        for activity in activities:
            act_type = activity.get("activity_type", "unknown")
            activity_breakdown[act_type] = activity_breakdown.get(act_type, 0) + 1
        
        return {
            "user": {
                "username": viewer["username"],
                "level": level,
                "total_points": total_points,
                "badges": viewer.get("badges", []),
                "member_since": viewer.get("created_at")
            },
            "stats": {
                "total_activities": len(activities),
                "points_last_30_days": sum(daily_points.values()),
                "average_daily_points": sum(daily_points.values()) / 30 if daily_points else 0
            },
            "daily_points_chart": daily_points,
            "activity_breakdown": activity_breakdown,
            "recent_activities": activities[:10]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@analytics_router.get("/leaderboard/compare/{user_id}")
async def compare_with_leaderboard(user_id: str):
    """Compare user stats with leaderboard"""
    try:
        db = get_database()
        
        viewer = await db.viewers.find_one({"user_id": user_id})
        if not viewer:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user rank
        higher_ranked = await db.viewers.count_documents({
            "points": {"$gt": viewer.get("points", 0)}
        })
        
        rank = higher_ranked + 1
        
        # Get total users
        total_users = await db.viewers.count_documents({})
        
        return {
            "your_rank": rank,
            "total_users": total_users,
            "percentile": round((1 - rank/total_users) * 100, 1) if total_users > 0 else 0,
            "your_points": viewer.get("points", 0),
            "your_level": viewer.get("level", 1)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing with leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
