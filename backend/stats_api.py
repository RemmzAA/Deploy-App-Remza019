"""
REMZA019 Gaming - Stats Dashboard
Analytics and metrics for streamers
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("stats")

stats_router = APIRouter(prefix="/stats", tags=["stats"])

class DailyStats(BaseModel):
    date: str
    viewers: int
    points_earned: int
    chat_messages: int
    new_subscribers: int

class EngagementMetrics(BaseModel):
    total_viewers: int
    active_viewers: int
    total_points: int
    avg_points_per_user: float
    chat_activity: int
    poll_participation: int
    prediction_participation: int

def get_database():
    from server import get_database as get_db
    return get_db()

@stats_router.get("/dashboard")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics - PUBLIC"""
    try:
        db = get_database()
        
        # Total viewers
        total_viewers = await db.viewers.count_documents({})
        
        # Active viewers (logged in last 24h)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        active_viewers = await db.viewers.count_documents({
            "last_active": {"$gte": yesterday}
        })
        
        # Total points distributed
        pipeline = [
            {"$group": {
                "_id": None,
                "total_points": {"$sum": "$points"},
                "avg_points": {"$avg": "$points"}
            }}
        ]
        points_data = await db.viewers.aggregate(pipeline).to_list(length=1)
        total_points = points_data[0].get("total_points", 0) if points_data else 0
        avg_points = points_data[0].get("avg_points", 0) if points_data else 0
        
        # Chat activity (from recent messages)
        # Note: This depends on chat_api storing messages in DB
        chat_count = 0  # Placeholder - implement based on chat storage
        
        # Poll & Prediction participation
        # Note: These are in-memory, but we can count from active items
        from polls_api import active_polls, poll_votes
        from predictions_api import active_predictions, prediction_votes
        
        poll_participation = sum(len(votes) for votes in poll_votes.values())
        prediction_participation = sum(len(votes) for votes in prediction_votes.values())
        
        metrics = EngagementMetrics(
            total_viewers=total_viewers,
            active_viewers=active_viewers,
            total_points=int(total_points),
            avg_points_per_user=round(avg_points, 1),
            chat_activity=chat_count,
            poll_participation=poll_participation,
            prediction_participation=prediction_participation
        )
        
        return metrics.dict()
        
    except Exception as e:
        logger.error(f"❌ Get dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")

@stats_router.get("/points-distribution")
async def get_points_distribution():
    """Get points distribution across viewer levels - PUBLIC"""
    try:
        db = get_database()
        
        # Group viewers by level and count points
        pipeline = [
            {
                "$group": {
                    "_id": "$level",
                    "count": {"$sum": 1},
                    "total_points": {"$sum": "$points"},
                    "avg_points": {"$avg": "$points"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        distribution = await db.viewers.aggregate(pipeline).to_list(length=10)
        
        result = []
        for item in distribution:
            result.append({
                "level": item["_id"],
                "viewers": item["count"],
                "total_points": item["total_points"],
                "avg_points": round(item["avg_points"], 1)
            })
        
        return {"distribution": result}
        
    except Exception as e:
        logger.error(f"❌ Get points distribution error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get points distribution")

@stats_router.get("/activity-chart")
async def get_activity_chart(days: int = 7):
    """Get daily activity chart data - PUBLIC"""
    try:
        db = get_database()
        
        # Generate date range
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
        dates.reverse()
        
        # Get viewer registrations per day
        daily_data = []
        for date_str in dates:
            date_start = f"{date_str}T00:00:00"
            date_end = f"{date_str}T23:59:59"
            
            # Count new viewers
            new_viewers = await db.viewers.count_documents({
                "created_at": {
                    "$gte": date_start,
                    "$lte": date_end
                }
            })
            
            # Count active viewers
            active = await db.viewers.count_documents({
                "last_active": {
                    "$gte": date_start,
                    "$lte": date_end
                }
            })
            
            daily_data.append({
                "date": date_str,
                "new_viewers": new_viewers,
                "active_viewers": active,
                "engagement": round((active / max(new_viewers, 1)) * 100, 1)
            })
        
        return {"chart_data": daily_data}
        
    except Exception as e:
        logger.error(f"❌ Get activity chart error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get activity chart")

@stats_router.get("/top-activities")
async def get_top_activities():
    """Get most popular activities by points earned - PUBLIC"""
    try:
        # Activity types and their point values
        activities = [
            {"name": "Subscribe", "points": 25, "icon": "🔔"},
            {"name": "Share Stream", "points": 10, "icon": "📤"},
            {"name": "Stream Prediction", "points": 7, "icon": "🎯"},
            {"name": "Stream View (5min)", "points": 5, "icon": "📺"},
            {"name": "Daily Visit", "points": 5, "icon": "📅"},
            {"name": "Vote in Poll", "points": 3, "icon": "🗳️"},
            {"name": "Like Video", "points": 3, "icon": "👍"},
            {"name": "Chat Message", "points": 2, "icon": "💬"}
        ]
        
        # Sort by points (already sorted, but for clarity)
        activities.sort(key=lambda x: x["points"], reverse=True)
        
        return {"activities": activities}
        
    except Exception as e:
        logger.error(f"❌ Get top activities error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top activities")

@stats_router.get("/engagement-rate")
async def get_engagement_rate():
    """Calculate overall engagement rate - PUBLIC"""
    try:
        db = get_database()
        
        total_viewers = await db.viewers.count_documents({})
        
        if total_viewers == 0:
            return {"engagement_rate": 0, "message": "No viewers yet"}
        
        # Active viewers (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        active_week = await db.viewers.count_documents({
            "last_active": {"$gte": week_ago}
        })
        
        # Viewers with points > 0
        engaged_viewers = await db.viewers.count_documents({
            "points": {"$gt": 0}
        })
        
        engagement_rate = (engaged_viewers / total_viewers * 100) if total_viewers > 0 else 0
        activity_rate = (active_week / total_viewers * 100) if total_viewers > 0 else 0
        
        return {
            "engagement_rate": round(engagement_rate, 1),
            "activity_rate": round(activity_rate, 1),
            "total_viewers": total_viewers,
            "engaged_viewers": engaged_viewers,
            "active_this_week": active_week
        }
        
    except Exception as e:
        logger.error(f"❌ Get engagement rate error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get engagement rate")
