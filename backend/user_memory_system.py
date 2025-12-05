"""
019 Solutions - Enhanced User & Admin Memory System
Comprehensive tracking and analytics for all users and admins
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os

logger = logging.getLogger(__name__)

class UserMemorySystem:
    """Enhanced memory system for tracking users and admins"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client.test_database
    
    async def log_user_activity(
        self,
        user_id: str,
        activity_type: str,
        details: Dict = None,
        ip_address: str = None,
        user_agent: str = None
    ):
        """Log user activity for analytics and security"""
        
        activity = {
            "user_id": user_id,
            "activity_type": activity_type,  # login, logout, registration, email_verification, etc.
            "timestamp": datetime.utcnow(),
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        await self.db.user_activity_log.insert_one(activity)
        logger.info(f"📝 Activity logged: {user_id} - {activity_type}")
    
    async def get_user_memory(self, user_id: str) -> Dict:
        """Get comprehensive user memory including stats and history"""
        
        # Get user data
        user = await self.db.viewers.find_one({"user_id": user_id}, {"_id": 0})
        
        if not user:
            return None
        
        # Get activity history
        activities = await self.db.user_activity_log.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(50).to_list(50)
        
        # Get active sessions
        sessions = await self.db.sessions.find({
            "user_id": user_id,
            "active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        }, {"_id": 0}).to_list(10)
        
        # Calculate stats
        total_activities = await self.db.user_activity_log.count_documents({"user_id": user_id})
        
        # Last login info
        last_login = await self.db.user_activity_log.find_one(
            {"user_id": user_id, "activity_type": "login"},
            sort=[("timestamp", -1)]
        )
        
        return {
            "user": user,
            "total_activities": total_activities,
            "recent_activities": activities,
            "active_sessions": sessions,
            "last_login": last_login.get("timestamp") if last_login else None,
            "session_count": len(sessions)
        }
    
    async def get_admin_memory(self, admin_username: str) -> Dict:
        """Get comprehensive admin memory including actions and stats"""
        
        # Get admin data
        admin = await self.db.admins.find_one({"username": admin_username}, {"_id": 0, "hashed_password": 0})
        
        if not admin:
            return None
        
        # Get admin actions
        actions = await self.db.admin_actions.find(
            {"admin_username": admin_username}
        ).sort("timestamp", -1).limit(100).to_list(100)
        
        # Get active sessions
        sessions = await self.db.sessions.find({
            "username": admin_username,
            "role": "admin",
            "active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        }, {"_id": 0}).to_list(10)
        
        # Calculate stats
        total_actions = await self.db.admin_actions.count_documents({"admin_username": admin_username})
        
        return {
            "admin": admin,
            "total_actions": total_actions,
            "recent_actions": actions,
            "active_sessions": sessions,
            "session_count": len(sessions)
        }
    
    async def log_admin_action(
        self,
        admin_username: str,
        action_type: str,
        description: str,
        affected_user: str = None,
        details: Dict = None
    ):
        """Log admin action for audit trail"""
        
        action = {
            "admin_username": admin_username,
            "action_type": action_type,  # ban, unban, modify_points, delete_content, etc.
            "description": description,
            "affected_user": affected_user,
            "timestamp": datetime.utcnow(),
            "details": details or {}
        }
        
        await self.db.admin_actions.insert_one(action)
        logger.info(f"👮 Admin action logged: {admin_username} - {action_type}")
    
    async def get_all_users_summary(self) -> Dict:
        """Get summary of all users for admin dashboard"""
        
        # Total counts
        total_users = await self.db.viewers.count_documents({})
        verified_users = await self.db.viewers.count_documents({"email_verified": True})
        active_sessions = await self.db.sessions.count_documents({
            "active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        # Recent registrations (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_registrations = await self.db.viewers.count_documents({
            "registration_date": {"$gte": seven_days_ago}
        })
        
        # Top users by points
        top_users = await self.db.viewers.find(
            {},
            {"_id": 0, "username": 1, "points": 1, "level": 1}
        ).sort("points", -1).limit(10).to_list(10)
        
        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "active_sessions": active_sessions,
            "recent_registrations": recent_registrations,
            "top_users": top_users
        }
    
    async def get_security_alerts(self) -> List[Dict]:
        """Get security alerts (multiple failed logins, suspicious activity)"""
        
        alerts = []
        
        # Multiple failed login attempts in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # Group by IP and count failed attempts
        pipeline = [
            {
                "$match": {
                    "activity_type": "failed_login",
                    "timestamp": {"$gte": one_hour_ago}
                }
            },
            {
                "$group": {
                    "_id": "$ip_address",
                    "count": {"$sum": 1},
                    "users": {"$addToSet": "$user_id"}
                }
            },
            {
                "$match": {"count": {"$gte": 5}}  # 5+ failed attempts
            }
        ]
        
        suspicious_ips = await self.db.user_activity_log.aggregate(pipeline).to_list(100)
        
        for item in suspicious_ips:
            alerts.append({
                "type": "multiple_failed_logins",
                "severity": "high",
                "ip_address": item["_id"],
                "attempt_count": item["count"],
                "affected_users": item["users"],
                "timestamp": datetime.utcnow()
            })
        
        return alerts
    
    async def cleanup_old_logs(self, days: int = 90):
        """Clean up activity logs older than specified days"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.user_activity_log.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        
        logger.info(f"🧹 Cleaned up {result.deleted_count} old activity logs")
        return result.deleted_count

# Global instance
_user_memory_system = None

def get_user_memory_system() -> UserMemorySystem:
    """Get or create user memory system instance"""
    global _user_memory_system
    if _user_memory_system is None:
        _user_memory_system = UserMemorySystem()
    return _user_memory_system
