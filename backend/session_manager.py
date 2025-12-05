"""
019 Solutions - Session Management System
Cookie-based persistent sessions for users and admins
"""
from fastapi import Request, Response, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import secrets
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Security
security = HTTPBearer()

class SessionManager:
    """Manage user and admin sessions with cookies"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL')
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client.remza019_gaming
        
    async def create_session(
        self, 
        user_id: str, 
        username: str, 
        role: str = "viewer",
        extra_data: Dict = None
    ) -> str:
        """Create new session and return JWT token"""
        
        # Create session document
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "username": username,
            "role": role,  # "viewer" or "admin"
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "active": True,
            **(extra_data or {})
        }
        
        # Store in database
        await self.db.sessions.insert_one(session_data)
        
        # Create JWT token
        token_data = {
            "sub": user_id,
            "session_id": session_id,
            "username": username,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        logger.info(f"✅ Session created for {username} ({role})")
        return token
    
    async def verify_session(self, token: str) -> Optional[Dict]:
        """Verify session token and return user data"""
        try:
            # Decode JWT
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            session_id = payload.get("session_id")
            user_id = payload.get("sub")
            
            # Check session in database
            session = await self.db.sessions.find_one({
                "session_id": session_id,
                "user_id": user_id,
                "active": True,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not session:
                return None
            
            # Update last active time
            await self.db.sessions.update_one(
                {"session_id": session_id},
                {"$set": {"last_active": datetime.utcnow()}}
            )
            
            return {
                "user_id": session["user_id"],
                "username": session["username"],
                "role": session["role"],
                "session_id": session_id
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.error(f"JWT error: {e}")
            return None
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate/logout session"""
        result = await self.db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"active": False, "logout_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def get_user_sessions(self, user_id: str) -> list:
        """Get all active sessions for a user"""
        sessions = await self.db.sessions.find({
            "user_id": user_id,
            "active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        }, {"_id": 0}).to_list(100)
        
        return sessions
    
    async def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        result = await self.db.sessions.delete_many({
            "$or": [
                {"expires_at": {"$lt": datetime.utcnow()}},
                {"active": False, "logout_at": {"$lt": datetime.utcnow() - timedelta(days=30)}}
            ]
        })
        
        logger.info(f"🧹 Cleaned up {result.deleted_count} expired sessions")
        return result.deleted_count

# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get or create session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

# Cookie helpers
def set_session_cookie(response: Response, token: str):
    """Set session cookie in response"""
    response.set_cookie(
        key="remza_session",
        value=token,
        httponly=True,  # Prevent XSS
        secure=True,    # HTTPS only
        samesite="lax", # CSRF protection
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 7 days in seconds
        path="/"
    )

def clear_session_cookie(response: Response):
    """Clear session cookie"""
    response.delete_cookie(key="remza_session", path="/")

async def get_current_user_from_cookie(request: Request) -> Optional[Dict]:
    """Get current user from session cookie"""
    token = request.cookies.get("remza_session")
    
    if not token:
        return None
    
    session_manager = get_session_manager()
    return await session_manager.verify_session(token)

async def require_viewer_auth(request: Request) -> Dict:
    """Require viewer authentication"""
    user = await get_current_user_from_cookie(request)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    return user

async def require_admin_auth(request: Request) -> Dict:
    """Require admin authentication"""
    user = await get_current_user_from_cookie(request)
    
    if not user or user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    
    return user
