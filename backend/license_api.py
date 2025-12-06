# License Management API - Backend License System
# REMZA019 Gaming - Customizable Streamer Website

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import secrets
import string
from motor.motor_asyncio import AsyncIOMotorClient
import os

router = APIRouter()

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
licenses_collection = db['licenses']

# Pydantic Models
class LicenseKey(BaseModel):
    license_key: str
    license_type: str  # "TRIAL", "BASIC", or "PREMIUM"
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    created_at: str
    activated_at: Optional[str] = None
    expires_at: Optional[str] = None
    is_active: bool = True
    payment_id: Optional[str] = None
    customization: Optional[dict] = None
    assigned_to: Optional[str] = None  # member_id
    assigned_email: Optional[str] = None
    assigned_nickname: Optional[str] = None

class GenerateLicenseRequest(BaseModel):
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    license_type: str = "TRIAL"  # "TRIAL", "BASIC", or "PREMIUM"
    duration_days: Optional[int] = None  # For TRIAL licenses

class VerifyLicenseRequest(BaseModel):
    license_key: str

class DeactivateLicenseRequest(BaseModel):
    license_key: str
    reason: Optional[str] = None

# Helper Functions
def generate_license_key(license_type: str = "FULL") -> str:
    """Generate a unique license key"""
    prefix = license_type.upper()
    
    # Generate 3 segments of 5 random uppercase alphanumeric characters
    chars = string.ascii_uppercase + string.digits
    segment1 = ''.join(secrets.choice(chars) for _ in range(5))
    segment2 = ''.join(secrets.choice(chars) for _ in range(5))
    segment3 = ''.join(secrets.choice(chars) for _ in range(5))
    
    return f"{prefix}-{segment1}-{segment2}-{segment3}"

# API Endpoints

@router.post("/api/license/generate")
async def generate_license(request: GenerateLicenseRequest):
    """
    Generate a new license key
    Admin only endpoint (add authentication later)
    """
    try:
        # Generate unique key
        license_key = generate_license_key(request.license_type)
        
        # Check if key already exists (very unlikely but possible)
        existing = await licenses_collection.find_one({"license_key": license_key})
        while existing:
            license_key = generate_license_key(request.license_type)
            existing = await licenses_collection.find_one({"license_key": license_key})
        
        # Create license document
        now = datetime.utcnow().isoformat()
        
        # Calculate expiration for TRIAL licenses
        expires_at = None
        if request.license_type == "TRIAL":
            trial_days = request.duration_days if request.duration_days else 7
            expires_at = (datetime.utcnow() + timedelta(days=trial_days)).isoformat()
        
        license_doc = {
            "license_key": license_key,
            "license_type": request.license_type,
            "user_email": request.user_email,
            "user_name": request.user_name,
            "created_at": now,
            "activated_at": None,
            "expires_at": expires_at,
            "is_active": True,
            "payment_id": None,
            "customization": None,
            "assigned_to": None,
            "assigned_email": None,
            "assigned_nickname": None
        }
        
        # Insert to database
        await licenses_collection.insert_one(license_doc)
        
        return {
            "success": True,
            "license_key": license_key,
            "license_type": request.license_type,
            "message": "License key generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating license: {str(e)}")

@router.post("/api/license/verify")
async def verify_license(request: VerifyLicenseRequest):
    """
    Verify a license key
    Public endpoint - used by frontend to validate keys
    """
    try:
        license_key = request.license_key.strip().upper()
        
        # Find license in database
        license_doc = await licenses_collection.find_one({"license_key": license_key})
        
        if not license_doc:
            return {
                "success": False,
                "valid": False,
                "message": "License key not found"
            }
        
        # Check if active
        if not license_doc.get("is_active", False):
            return {
                "success": False,
                "valid": False,
                "message": "License key has been deactivated"
            }
        
        # Check if expired (for TRIAL keys)
        if license_doc.get("license_type") == "TRIAL":
            expires_at = license_doc.get("expires_at")
            if expires_at:
                expiry_date = datetime.fromisoformat(expires_at)
                if datetime.utcnow() > expiry_date:
                    # Auto-deactivate expired trial
                    await licenses_collection.update_one(
                        {"license_key": license_key},
                        {"$set": {"is_active": False}}
                    )
                    return {
                        "success": False,
                        "valid": False,
                        "message": "Trial license has expired"
                    }
        
        # Update activation timestamp if first time
        if not license_doc.get("activated_at"):
            await licenses_collection.update_one(
                {"license_key": license_key},
                {"$set": {"activated_at": datetime.utcnow().isoformat()}}
            )
        
        return {
            "success": True,
            "valid": True,
            "license_type": license_doc.get("license_type"),
            "user_email": license_doc.get("user_email"),
            "user_name": license_doc.get("user_name"),
            "created_at": license_doc.get("created_at"),
            "activated_at": license_doc.get("activated_at"),
            "expires_at": license_doc.get("expires_at"),
            "message": "License key is valid"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying license: {str(e)}")

@router.get("/api/license/list")
async def list_licenses():
    """
    List all licenses
    Admin only endpoint (add authentication later)
    """
    try:
        licenses = await licenses_collection.find().sort("created_at", -1).to_list(length=1000)
        
        # Remove MongoDB _id field
        for license in licenses:
            license['_id'] = str(license['_id'])
        
        return {
            "success": True,
            "licenses": licenses,
            "total": len(licenses)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing licenses: {str(e)}")

@router.post("/api/license/deactivate")
async def deactivate_license(request: DeactivateLicenseRequest):
    """
    Deactivate a license key
    Admin only endpoint (add authentication later)
    """
    try:
        license_key = request.license_key.strip().upper()
        
        # Find license
        license_doc = await licenses_collection.find_one({"license_key": license_key})
        
        if not license_doc:
            return {
                "success": False,
                "message": "License key not found"
            }
        
        # Deactivate
        update_data = {
            "is_active": False,
            "deactivated_at": datetime.utcnow().isoformat()
        }
        
        if request.reason:
            update_data["deactivation_reason"] = request.reason
        
        await licenses_collection.update_one(
            {"license_key": license_key},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": "License key deactivated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating license: {str(e)}")

@router.get("/api/license/stats")
async def get_license_stats():
    """
    Get license statistics
    Admin only endpoint
    """
    try:
        total = await licenses_collection.count_documents({})
        active = await licenses_collection.count_documents({"is_active": True})
        trial = await licenses_collection.count_documents({"license_type": "TRIAL"})
        basic = await licenses_collection.count_documents({"license_type": "BASIC"})
        premium = await licenses_collection.count_documents({"license_type": "PREMIUM"})
        activated = await licenses_collection.count_documents({"activated_at": {"$ne": None}})
        assigned = await licenses_collection.count_documents({"assigned_to": {"$ne": None}})
        
        return {
            "success": True,
            "stats": {
                "total": total,
                "active": active,
                "inactive": total - active,
                "trial": trial,
                "basic": basic,
                "premium": premium,
                "activated": activated,
                "never_activated": total - activated,
                "assigned_to_members": assigned
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.delete("/api/license/delete/{license_key}")
async def delete_license(license_key: str):
    """
    Permanently delete a license key
    Admin only endpoint - USE WITH CAUTION
    """
    try:
        license_key = license_key.strip().upper()
        
        result = await licenses_collection.delete_one({"license_key": license_key})
        
        if result.deleted_count == 0:
            return {
                "success": False,
                "message": "License key not found"
            }
        
        return {
            "success": True,
            "message": "License key deleted permanently"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting license: {str(e)}")


@router.get("/api/license/status")
async def get_license_status():
    """
    Get current active license status
    Returns the most recently activated license
    """
    try:
        # Find most recently activated license
        license_doc = await licenses_collection.find_one(
            {"is_active": True},
            sort=[("activated_at", -1)]
        )
        
        if not license_doc:
            return {
                "is_active": False,
                "message": "No active license found"
            }
        
        # Remove MongoDB _id
        if "_id" in license_doc:
            del license_doc["_id"]
        
        return license_doc
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching license status: {str(e)}")

@router.post("/api/license/activate")
async def activate_license(request: VerifyLicenseRequest):
    """
    Activate a license key
    Same as verify but with activation semantics
    """
    try:
        license_key = request.license_key.strip().upper()
        
        # Find license in database
        license_doc = await licenses_collection.find_one({"license_key": license_key})
        
        if not license_doc:
            return {
                "success": False,
                "message": "License key not found"
            }
        
        # Check if already active
        if not license_doc.get("is_active", False):
            return {
                "success": False,
                "message": "License key has been deactivated"
            }
        
        # Check if expired (for TRIAL keys)
        if license_doc.get("license_type") == "TRIAL":
            expires_at = license_doc.get("expires_at")
            if expires_at:
                expiry_date = datetime.fromisoformat(expires_at)
                if datetime.utcnow() > expiry_date:
                    return {
                        "success": False,
                        "message": "Trial license has expired"
                    }
        
        # Update activation timestamp
        now = datetime.utcnow().isoformat()
        await licenses_collection.update_one(
            {"license_key": license_key},
            {"$set": {"activated_at": now}}
        )
        
        # Refresh license data
        license_doc = await licenses_collection.find_one({"license_key": license_key}, {"_id": 0})
        
        return {
            "success": True,
            "message": "License activated successfully",
            "license": license_doc
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activating license: {str(e)}")

