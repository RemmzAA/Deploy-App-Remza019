# Member Management API - REMZA019 Gaming
# JWT Authentication + Discord Integration

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import jwt
import secrets
import string
import hashlib
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['remza019_gaming']
members_collection = db['members']
licenses_collection = db['licenses']

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'remza019_member_secret_key_2024')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRE_HOURS = 24 * 7  # 7 days

router = APIRouter(prefix="/api/member", tags=["member"])
security = HTTPBearer()

# Pydantic Models
class MemberRegistration(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=30)
    discord_id: str = Field(..., min_length=10, max_length=30)
    email: EmailStr

class MemberLogin(BaseModel):
    email: EmailStr
    verification_code: Optional[str] = None

class ActivateLicenseRequest(BaseModel):
    license_key: str

class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None

# Helper Functions
def generate_verification_code() -> str:
    """Generate 6-digit verification code"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def generate_member_id() -> str:
    """Generate unique member ID"""
    return 'MEM-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def create_jwt_token(member_id: str, email: str) -> str:
    """Create JWT token for member"""
    payload = {
        'member_id': member_id,
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return member data"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        member_id = payload.get('member_id')
        if not member_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get member from database
        member = await members_collection.find_one({"member_id": member_id}, {"_id": 0})
        if not member:
            raise HTTPException(status_code=401, detail="Member not found")
        
        if not member.get('is_active', True):
            raise HTTPException(status_code=403, detail="Account is banned")
        
        return member
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# API Endpoints

@router.post("/register")
async def register_member(data: MemberRegistration):
    """
    Register new member with nickname, Discord ID, and email
    """
    try:
        # Check if email already exists
        existing_email = await members_collection.find_one({"email": data.email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if Discord ID already exists
        existing_discord = await members_collection.find_one({"discord_id": data.discord_id})
        if existing_discord:
            raise HTTPException(status_code=400, detail="Discord ID already registered")
        
        # Check if nickname already exists
        existing_nickname = await members_collection.find_one({"nickname": data.nickname})
        if existing_nickname:
            raise HTTPException(status_code=400, detail="Nickname already taken")
        
        # Generate member ID and verification code
        member_id = generate_member_id()
        verification_code = generate_verification_code()
        
        # Create member document
        now = datetime.now(timezone.utc).isoformat()
        member_doc = {
            "member_id": member_id,
            "nickname": data.nickname,
            "discord_id": data.discord_id,
            "email": data.email,
            "email_verified": False,
            "verification_code": verification_code,
            "points": 0,
            "level": 1,
            "level_name": "Novice",
            "license_type": "NONE",
            "license_key": None,
            "license_expires_at": None,
            "is_active": True,
            "is_banned": False,
            "avatar_url": None,
            "created_at": now,
            "updated_at": now,
            "last_login": None
        }
        
        # Insert to database
        await members_collection.insert_one(member_doc)
        
        # TODO: Send verification email with code
        logger.info(f"Member registered: {data.email} - Verification code: {verification_code}")
        
        return {
            "success": True,
            "message": "Registration successful! Please check your email for verification code.",
            "member_id": member_id,
            "verification_code": verification_code  # In production, remove this and send via email
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/verify-email")
async def verify_email(email: EmailStr, code: str):
    """
    Verify email with verification code
    """
    try:
        member = await members_collection.find_one({"email": email})
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        if member.get("email_verified"):
            return {
                "success": True,
                "message": "Email already verified",
                "already_verified": True
            }
        
        if member.get("verification_code") != code:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        # Update member as verified
        await members_collection.update_one(
            {"email": email},
            {"$set": {
                "email_verified": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Create JWT token
        token = create_jwt_token(member['member_id'], email)
        
        return {
            "success": True,
            "message": "Email verified successfully!",
            "token": token,
            "member": {
                "member_id": member['member_id'],
                "nickname": member['nickname'],
                "email": member['email'],
                "discord_id": member['discord_id'],
                "points": member['points'],
                "level": member['level']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@router.post("/login")
async def login_member(data: MemberLogin):
    """
    Login member with email (passwordless - sends verification code)
    """
    try:
        member = await members_collection.find_one({"email": data.email})
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found. Please register first.")
        
        if not member.get('is_active', True) or member.get('is_banned', False):
            raise HTTPException(status_code=403, detail="Account is banned or inactive")
        
        # If verification code provided, verify and login
        if data.verification_code:
            if member.get('verification_code') != data.verification_code:
                raise HTTPException(status_code=400, detail="Invalid verification code")
            
            # Update last login
            await members_collection.update_one(
                {"email": data.email},
                {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
            )
            
            # Create JWT token
            token = create_jwt_token(member['member_id'], data.email)
            
            return {
                "success": True,
                "message": "Login successful!",
                "token": token,
                "member": {
                    "member_id": member['member_id'],
                    "nickname": member['nickname'],
                    "email": member['email'],
                    "discord_id": member['discord_id'],
                    "points": member['points'],
                    "level": member['level'],
                    "license_type": member.get('license_type', 'NONE')
                }
            }
        
        # Otherwise, generate and send new verification code
        new_code = generate_verification_code()
        await members_collection.update_one(
            {"email": data.email},
            {"$set": {"verification_code": new_code}}
        )
        
        # TODO: Send verification code via email
        logger.info(f"Login attempt for {data.email} - Verification code: {new_code}")
        
        return {
            "success": True,
            "message": "Verification code sent to your email!",
            "verification_code": new_code,  # In production, remove this
            "requires_verification": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/profile")
async def get_profile(member = Depends(verify_token)):
    """
    Get current member profile
    """
    return {
        "success": True,
        "member": member
    }

@router.put("/profile")
async def update_profile(data: UpdateProfileRequest, member = Depends(verify_token)):
    """
    Update member profile
    """
    try:
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        if data.nickname:
            # Check if nickname is taken by another member
            existing = await members_collection.find_one({
                "nickname": data.nickname,
                "member_id": {"$ne": member['member_id']}
            })
            if existing:
                raise HTTPException(status_code=400, detail="Nickname already taken")
            update_data['nickname'] = data.nickname
        
        if data.avatar_url:
            update_data['avatar_url'] = data.avatar_url
        
        # Update member
        await members_collection.update_one(
            {"member_id": member['member_id']},
            {"$set": update_data}
        )
        
        # Get updated member
        updated_member = await members_collection.find_one(
            {"member_id": member['member_id']},
            {"_id": 0}
        )
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "member": updated_member
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.post("/activate-license")
async def activate_member_license(data: ActivateLicenseRequest, member = Depends(verify_token)):
    """
    Activate a license key for current member
    """
    try:
        license_key = data.license_key.strip().upper()
        
        # Check if license exists and is valid
        license_doc = await licenses_collection.find_one({"license_key": license_key})
        
        if not license_doc:
            raise HTTPException(status_code=404, detail="License key not found")
        
        if not license_doc.get('is_active', False):
            raise HTTPException(status_code=400, detail="License key has been deactivated")
        
        # Check if already assigned to another member
        if license_doc.get('assigned_to') and license_doc['assigned_to'] != member['member_id']:
            raise HTTPException(status_code=400, detail="License key already assigned to another member")
        
        # Check expiration for TRIAL
        license_type = license_doc.get('license_type', 'TRIAL')
        expires_at = license_doc.get('expires_at')
        
        if license_type == 'TRIAL' and expires_at:
            expiry_date = datetime.fromisoformat(expires_at)
            if datetime.now(timezone.utc) > expiry_date:
                raise HTTPException(status_code=400, detail="License key has expired")
        
        # Activate license for member
        now = datetime.now(timezone.utc).isoformat()
        
        # Update license
        await licenses_collection.update_one(
            {"license_key": license_key},
            {"$set": {
                "assigned_to": member['member_id'],
                "assigned_email": member['email'],
                "assigned_nickname": member['nickname'],
                "activated_at": now
            }}
        )
        
        # Update member
        await members_collection.update_one(
            {"member_id": member['member_id']},
            {"$set": {
                "license_type": license_type,
                "license_key": license_key,
                "license_expires_at": expires_at,
                "updated_at": now
            }}
        )
        
        return {
            "success": True,
            "message": "License activated successfully!",
            "license_type": license_type,
            "expires_at": expires_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License activation error: {e}")
        raise HTTPException(status_code=500, detail=f"Activation failed: {str(e)}")

@router.get("/stats")
async def get_member_stats(member = Depends(verify_token)):
    """
    Get member statistics
    """
    try:
        return {
            "success": True,
            "stats": {
                "points": member.get('points', 0),
                "level": member.get('level', 1),
                "level_name": member.get('level_name', 'Novice'),
                "license_type": member.get('license_type', 'NONE'),
                "member_since": member.get('created_at'),
                "last_login": member.get('last_login')
            }
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
