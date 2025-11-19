"""
Version Manager API for REMZA019 Gaming
Handles version management and updates
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

version_router = APIRouter(prefix="/api/version", tags=["version"])

class VersionInfo(BaseModel):
    version: str
    build_date: str
    environment: str

@version_router.get("/info")
async def get_version_info():
    """Get current version information"""
    return VersionInfo(
        version="3.0.0",
        build_date=datetime.utcnow().isoformat(),
        environment="production"
    )