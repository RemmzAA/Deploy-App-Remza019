"""
REMZA019 Gaming - Version Management API
Simple version tracking for app updates
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger("version_api")

version_router = APIRouter(prefix="/version", tags=["version"])

# Current app version
CURRENT_VERSION = "1.0.0"

class VersionResponse(BaseModel):
    version: str
    release_date: str
    features: list[str]

class UpdateCheckResponse(BaseModel):
    update_available: bool
    current_version: str
    latest_version: str
    message: str

@version_router.get("/current")
async def get_current_version():
    """Get current app version"""
    return VersionResponse(
        version=CURRENT_VERSION,
        release_date="2025-01-20",
        features=[
            "YouTube Integration",
            "OBS Remote Control",
            "Email Notifications",
            "Theme System",
            "Viewer Gamification"
        ]
    )

@version_router.get("/check-update")
async def check_for_updates(current_version: Optional[str] = None):
    """Check if updates are available"""
    return UpdateCheckResponse(
        update_available=False,
        current_version=current_version or CURRENT_VERSION,
        latest_version=CURRENT_VERSION,
        message="You are running the latest version!"
    )
