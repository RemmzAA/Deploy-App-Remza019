"""
Version Manager API for REMZA019 Gaming
Handles version management and updates
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

version_router = APIRouter(prefix="/api/version", tags=["version"])

# Current version
CURRENT_VERSION = "1.5.0"
BUILD_DATE = "2025-01-10"

class VersionInfo(BaseModel):
    version: str
    build_date: str
    environment: str
    features: list

@version_router.get("/current")
async def get_current_version():
    """Get current version"""
    return {
        "success": True,
        "version": CURRENT_VERSION,
        "build_date": BUILD_DATE,
        "environment": "production"
    }

@version_router.get("/check-update")
async def check_for_updates(current_version: str = CURRENT_VERSION):
    """Check if updates are available"""
    return {
        "success": True,
        "has_update": False,
        "current_version": CURRENT_VERSION,
        "latest_version": CURRENT_VERSION,
        "message": "You are running the latest version"
    }

@version_router.get("/info")
async def get_version_info():
    """Get detailed version information"""
    return {
        "success": True,
        "data": {
            "version": CURRENT_VERSION,
            "build_date": BUILD_DATE,
            "environment": "production",
            "features": [
                "Theme Switcher (6 themes)",
                "Real-time Admin Control",
                "PWA Support",
                "Cookie/Session Management",
                "Service Worker v1.5.0",
                "Donation System",
                "Viewer System"
            ]
        }
    }