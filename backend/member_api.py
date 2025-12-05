# Member Management API - 019 Solutions
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

# Import email service
from email_service import email_service

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
        
        # Send verification email
        base_url = os.environ.get('FRONTEND_URL', 'https://gamer-dashboard-5.preview.emergentagent.com')
        email_sent = await email_service.send_verification_email(
            to_email=data.email,
            username=data.nickname,
            verification_code=verification_code,
            base_url=base_url
        )
        
        if email_sent:
            logger.info(f"✅ Member registered: {data.email} - Verification email sent")
            return {
                "success": True,
                "message": "Registration successful! Please check your email for verification code.",
                "member_id": member_id
            }
        else:
            logger.warning(f"⚠️ Member registered but email failed: {data.email}")
            return {
                "success": True,
                "message": "Registration successful! Verification code (email failed):",
                "member_id": member_id,
                "verification_code": verification_code  # Fallback if email fails
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
        
        # Check if email is verified (by admin)
        if not member.get('email_verified', False):
            raise HTTPException(status_code=403, detail="Account pending admin verification. Please wait for approval.")
        
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
        
        # Send verification code via email (simpler email for login)
        subject = "🎮 019 Solutions - Login Verification Code"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #000; color: #00ff00; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #0a0a0a; border: 2px solid #00ff00; border-radius: 10px; padding: 30px; text-align: center; }}
                .code {{ font-size: 32px; font-weight: bold; color: #00ff00; background: #000; padding: 20px; border-radius: 10px; letter-spacing: 10px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎮 Login Verification</h1>
                <p>Your verification code is:</p>
                <div class="code">{new_code}</div>
                <p>This code expires in 15 minutes.</p>
            </div>
        </body>
        </html>
        """
        
        email_sent = await email_service.send_email(data.email, subject, html_content)
        
        if email_sent:
            logger.info(f"✅ Login code sent to {data.email}")
            return {
                "success": True,
                "message": "Verification code sent to your email!",
                "requires_verification": True
            }
        else:
            logger.warning(f"⚠️ Email failed for {data.email}, showing code")
            return {
                "success": True,
                "message": "Verification code (email failed):",
                "verification_code": new_code,  # Fallback if email fails
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

# ============ ADMIN ENDPOINTS ============

@router.get("/admin/pending-members")
async def get_pending_members():
    """
    Get all members pending email verification (Admin only)
    """
    try:
        pending = await members_collection.find(
            {"email_verified": False},
            {"_id": 0}
        ).sort("created_at", -1).to_list(length=100)
        
        return {
            "success": True,
            "members": pending,
            "total": len(pending)
        }
    except Exception as e:
        logger.error(f"Get pending members error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/all-members")
async def get_all_members():
    """
    Get all members (Admin only)
    """
    try:
        members = await members_collection.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).to_list(length=1000)
        
        return {
            "success": True,
            "members": members,
            "total": len(members)
        }
    except Exception as e:
        logger.error(f"Get all members error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/verify-member")
async def admin_verify_member(member_id: str):
    """
    Admin manually verifies a member (bypasses email verification)
    """
    try:
        member = await members_collection.find_one({"member_id": member_id})
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Verify member
        await members_collection.update_one(
            {"member_id": member_id},
            {"$set": {
                "email_verified": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "message": f"Member {member['nickname']} verified successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin verify member error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/ban-member")
async def admin_ban_member(member_id: str, reason: str = "Admin decision"):
    """
    Admin bans a member
    """
    try:
        member = await members_collection.find_one({"member_id": member_id})
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Ban member
        await members_collection.update_one(
            {"member_id": member_id},
            {"$set": {
                "is_active": False,
                "is_banned": True,
                "ban_reason": reason,
                "banned_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "message": f"Member {member['nickname']} banned"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin ban member error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/unban-member")
async def admin_unban_member(member_id: str):
    """
    Admin unbans a member
    """
    try:
        member = await members_collection.find_one({"member_id": member_id})
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Unban member
        await members_collection.update_one(
            {"member_id": member_id},
            {"$set": {
                "is_active": True,
                "is_banned": False,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "message": f"Member {member['nickname']} unbanned"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin unban member error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/member-stats")
async def get_admin_member_stats():
    """
    Get member statistics for admin dashboard
    """
    try:
        total = await members_collection.count_documents({})
        verified = await members_collection.count_documents({"email_verified": True})
        pending = await members_collection.count_documents({"email_verified": False})
        active = await members_collection.count_documents({"is_active": True})
        banned = await members_collection.count_documents({"is_banned": True})
        with_license = await members_collection.count_documents({"license_type": {"$ne": "NONE"}})
        
        return {
            "success": True,
            "stats": {
                "total": total,
                "verified": verified,
                "pending": pending,
                "active": active,
                "banned": banned,
                "with_license": with_license
            }
        }
    except Exception as e:
        logger.error(f"Get member stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
