"""
REMZA019 Gaming - Security Middleware
Input validation, sanitization, rate limiting, and security headers
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict
import re
import html
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)

# Rate limiting storage
rate_limit_storage = defaultdict(list)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text:
        return ""
    
    # Limit length
    text = text[:max_length]
    
    # Remove dangerous characters
    text = html.escape(text)
    
    # Remove script tags and other dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onload\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        r'eval\(',
        r'expression\(',
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    return text.strip()

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or len(username) < 3 or len(username) > 30:
        return False
    
    # Only alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False
    
    return True

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or len(email) > 100:
        return False
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False
    
    return True

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return True  # Empty URL is OK
    
    if len(url) > 500:
        return False
    
    # Must start with http:// or https://
    url_pattern = r'^https?://[^\s]+$'
    if not re.match(url_pattern, url):
        return False
    
    # Block localhost and internal IPs (SSRF prevention)
    dangerous_hosts = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '192.168.',
        '10.',
        '172.16.',
        'internal',
    ]
    
    for host in dangerous_hosts:
        if host in url.lower():
            return False
    
    return True

def validate_hex_color(color: str) -> bool:
    """Validate hex color code"""
    if not color:
        return False
    
    # Must be #RRGGBB format
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return False
    
    return True

def validate_points(points: int) -> bool:
    """Validate point value"""
    if not isinstance(points, int):
        return False
    
    # Points must be between -1000 and 1000
    if points < -1000 or points > 1000:
        return False
    
    return True

def rate_limit(identifier: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
    """Rate limiting - returns True if allowed, False if rate limited"""
    now = datetime.utcnow()
    
    # Clean old entries
    cutoff = now - timedelta(seconds=window_seconds)
    rate_limit_storage[identifier] = [
        timestamp for timestamp in rate_limit_storage[identifier]
        if timestamp > cutoff
    ]
    
    # Check limit
    if len(rate_limit_storage[identifier]) >= max_requests:
        return False
    
    # Add current request
    rate_limit_storage[identifier].append(now)
    return True

def check_rate_limit(request: Request, max_requests: int = 60) -> None:
    """Check rate limit and raise exception if exceeded"""
    client_ip = request.client.host if request.client else "unknown"
    identifier = hashlib.md5(f"{client_ip}:{request.url.path}".encode()).hexdigest()
    
    if not rate_limit(identifier, max_requests):
        logger.warning(f"⚠️ Rate limit exceeded for {client_ip} on {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )

def sanitize_config_update(data: Dict) -> Dict:
    """Sanitize viewer config update data"""
    sanitized = {}
    
    if "points_config" in data:
        sanitized["points_config"] = {}
        for activity, config in data["points_config"].items():
            # Sanitize activity name
            activity_clean = sanitize_input(activity, 50)
            
            # Validate config structure
            if not isinstance(config, dict):
                continue
            
            sanitized_config = {}
            
            # Validate points
            if "points" in config and validate_points(config["points"]):
                sanitized_config["points"] = int(config["points"])
            
            # Sanitize name
            if "name" in config:
                sanitized_config["name"] = sanitize_input(config["name"], 100)
            
            # Validate enabled
            if "enabled" in config:
                sanitized_config["enabled"] = bool(config["enabled"])
            
            # Sanitize icon (emoji)
            if "icon" in config:
                icon = config["icon"]
                # Allow only single emoji or short text
                if len(icon) <= 10:
                    sanitized_config["icon"] = sanitize_input(icon, 10)
            
            if sanitized_config:
                sanitized["points_config"][activity_clean] = sanitized_config
    
    if "level_system" in data:
        sanitized["level_system"] = {}
        for level, config in data["level_system"].items():
            # Validate level number
            try:
                level_num = int(level)
                if level_num < 1 or level_num > 10:
                    continue
            except (ValueError, TypeError):
                continue
            
            sanitized_config = {}
            
            # Validate required points
            if "required" in config and validate_points(config["required"]):
                sanitized_config["required"] = int(config["required"])
            
            # Sanitize name
            if "name" in config:
                sanitized_config["name"] = sanitize_input(config["name"], 50)
            
            # Validate features (array of strings)
            if "features" in config and isinstance(config["features"], list):
                sanitized_config["features"] = [
                    sanitize_input(f, 30) for f in config["features"][:20]
                ]
            
            # Sanitize icon
            if "icon" in config:
                icon = config["icon"]
                if len(icon) <= 10:
                    sanitized_config["icon"] = sanitize_input(icon, 10)
            
            if sanitized_config:
                sanitized["level_system"][str(level_num)] = sanitized_config
    
    if "rewards" in data:
        sanitized["rewards"] = {}
        for level, reward in data["rewards"].items():
            level_clean = sanitize_input(level, 20)
            
            if isinstance(reward, dict):
                sanitized_reward = {}
                
                if "reward" in reward:
                    sanitized_reward["reward"] = sanitize_input(reward["reward"], 200)
                
                if "description" in reward:
                    sanitized_reward["description"] = sanitize_input(reward["description"], 500)
                
                if sanitized_reward:
                    sanitized["rewards"][level_clean] = sanitized_reward
    
    if "system_settings" in data:
        settings = data["system_settings"]
        sanitized["system_settings"] = {}
        
        # Only boolean settings allowed
        bool_settings = [
            "enable_viewer_system",
            "enable_leaderboard",
            "enable_chat",
            "enable_notifications"
        ]
        
        for setting in bool_settings:
            if setting in settings:
                sanitized["system_settings"][setting] = bool(settings[setting])
        
        # Integer settings with limits
        if "max_leaderboard_entries" in settings:
            value = int(settings["max_leaderboard_entries"])
            if 10 <= value <= 500:
                sanitized["system_settings"]["max_leaderboard_entries"] = value
        
        if "daily_login_streak_bonus" in settings:
            value = int(settings["daily_login_streak_bonus"])
            if 0 <= value <= 100:
                sanitized["system_settings"]["daily_login_streak_bonus"] = value
    
    return sanitized

# Export functions
__all__ = [
    'SecurityMiddleware',
    'sanitize_input',
    'validate_username',
    'validate_email',
    'validate_url',
    'validate_hex_color',
    'validate_points',
    'rate_limit',
    'check_rate_limit',
    'sanitize_config_update'
]
