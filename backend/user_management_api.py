"""
REMZA019 Gaming - User Management API
Advanced user tracking, analytics, and management
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
import logging

from session_manager import require_admin_auth, get_current_user_from_cookie
from user_memory_system import get_user_memory_system

logger = logging.getLogger(__name__)

user_mgmt_router = APIRouter(prefix="/api/user-management", tags=["user-management"])

@user_mgmt_router.get("/users/summary")
async def get_users_summary(admin: dict = Depends(require_admin_auth)):
    """Get summary of all users (Admin only)"""
    try:
        memory_system = get_user_memory_system()
        summary = await memory_system.get_all_users_summary()
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Failed to get users summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user summary")

@user_mgmt_router.get("/users/{user_id}/memory")
async def get_user_memory(
    user_id: str,
    admin: dict = Depends(require_admin_auth)
):
    """Get detailed user memory and activity (Admin only)"""
    try:
        memory_system = get_user_memory_system()
        memory = await memory_system.get_user_memory(user_id)
        
        if not memory:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "data": memory
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user memory")

@user_mgmt_router.get("/admin/{username}/memory")
async def get_admin_memory(
    username: str,
    admin: dict = Depends(require_admin_auth)
):
    """Get detailed admin memory and actions (Admin only)"""
    try:
        memory_system = get_user_memory_system()
        memory = await memory_system.get_admin_memory(username)
        
        if not memory:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        return {
            "success": True,
            "data": memory
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get admin memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin memory")

@user_mgmt_router.get("/security/alerts")
async def get_security_alerts(admin: dict = Depends(require_admin_auth)):
    """Get security alerts (Admin only)"""
    try:
        memory_system = get_user_memory_system()
        alerts = await memory_system.get_security_alerts()
        
        return {
            "success": True,
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Failed to get security alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch security alerts")

@user_mgmt_router.get("/me/memory")
async def get_my_memory(request: Request):
    """Get current user's own memory and activity"""
    try:
        user = await get_current_user_from_cookie(request)
        
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        memory_system = get_user_memory_system()
        
        if user["role"] == "admin":
            memory = await memory_system.get_admin_memory(user["username"])
        else:
            memory = await memory_system.get_user_memory(user["user_id"])
        
        if not memory:
            raise HTTPException(status_code=404, detail="User data not found")
        
        return {
            "success": True,
            "data": memory
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch memory")
