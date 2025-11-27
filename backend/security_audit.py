"""
REMZA019 Gaming - Security Audit System
Comprehensive security checks and email verification enhancements
"""
import re
from typing import Dict, List
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)

class SecurityAuditor:
    """Security audit and validation system"""
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict:
        """Validate password strength and return detailed feedback"""
        
        feedback = {
            "is_valid": False,
            "score": 0,
            "issues": [],
            "suggestions": []
        }
        
        # Minimum length check
        if len(password) < 8:
            feedback["issues"].append("Password must be at least 8 characters long")
        else:
            feedback["score"] += 25
        
        # Uppercase check
        if not re.search(r'[A-Z]', password):
            feedback["issues"].append("Password should contain at least one uppercase letter")
        else:
            feedback["score"] += 25
        
        # Lowercase check
        if not re.search(r'[a-z]', password):
            feedback["issues"].append("Password should contain at least one lowercase letter")
        else:
            feedback["score"] += 25
        
        # Number check
        if not re.search(r'\d', password):
            feedback["issues"].append("Password should contain at least one number")
        else:
            feedback["score"] += 15
        
        # Special character check
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            feedback["suggestions"].append("Consider adding special characters for extra security")
        else:
            feedback["score"] += 10
        
        # Check for common patterns
        common_patterns = ['123456', 'password', 'qwerty', 'abc123']
        if any(pattern in password.lower() for pattern in common_patterns):
            feedback["issues"].append("Password contains common patterns")
            feedback["score"] -= 20
        
        # Determine if valid (score >= 75 and no critical issues)
        feedback["is_valid"] = feedback["score"] >= 75 and len(feedback["issues"]) == 0
        
        if feedback["is_valid"]:
            feedback["message"] = "Strong password! ✅"
        elif feedback["score"] >= 50:
            feedback["message"] = "Moderate password strength ⚠️"
        else:
            feedback["message"] = "Weak password ❌"
        
        return feedback
    
    @staticmethod
    def validate_username(username: str) -> Dict:
        """Validate username format and content"""
        
        feedback = {
            "is_valid": True,
            "issues": []
        }
        
        # Length check
        if len(username) < 3:
            feedback["is_valid"] = False
            feedback["issues"].append("Username must be at least 3 characters long")
        
        if len(username) > 20:
            feedback["is_valid"] = False
            feedback["issues"].append("Username must not exceed 20 characters")
        
        # Character check (alphanumeric + underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            feedback["is_valid"] = False
            feedback["issues"].append("Username can only contain letters, numbers, and underscores")
        
        # Must start with letter
        if not username[0].isalpha():
            feedback["is_valid"] = False
            feedback["issues"].append("Username must start with a letter")
        
        # Check for inappropriate content
        inappropriate_words = ['admin', 'moderator', 'system', 'remza019', 'official']
        if any(word in username.lower() for word in inappropriate_words):
            feedback["is_valid"] = False
            feedback["issues"].append("Username contains reserved words")
        
        return feedback
    
    @staticmethod
    def validate_email(email: str) -> Dict:
        """Validate email format"""
        
        feedback = {
            "is_valid": True,
            "issues": []
        }
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            feedback["is_valid"] = False
            feedback["issues"].append("Invalid email format")
        
        # Check for disposable email domains
        disposable_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        email_domain = email.split('@')[-1].lower()
        
        if email_domain in disposable_domains:
            feedback["is_valid"] = False
            feedback["issues"].append("Disposable email addresses are not allowed")
        
        return feedback
    
    @staticmethod
    def generate_secure_verification_code(length: int = 8) -> str:
        """Generate cryptographically secure verification code"""
        return secrets.token_urlsafe(length * 2)[:length].upper()
    
    @staticmethod
    def check_rate_limiting(user_id: str, action: str, max_attempts: int = 5, window_minutes: int = 15) -> Dict:
        """
        Check if user has exceeded rate limit for specific action
        Note: This is a placeholder - actual implementation would use Redis or database
        """
        
        return {
            "allowed": True,
            "remaining_attempts": max_attempts,
            "reset_time": datetime.utcnow() + timedelta(minutes=window_minutes)
        }
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]*>', '', input_string)
        
        # Remove script tags and content
        sanitized = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', sanitized, flags=re.IGNORECASE)
        
        # Remove SQL injection attempts
        sql_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', 'UNION', 'CREATE']
        for keyword in sql_keywords:
            sanitized = re.sub(rf'\b{keyword}\b', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @staticmethod
    def audit_session(session_data: Dict) -> Dict:
        """Audit session for suspicious activity"""
        
        audit_result = {
            "is_suspicious": False,
            "warnings": [],
            "risk_score": 0
        }
        
        # Check session age
        created_at = session_data.get("created_at")
        if created_at:
            age = datetime.utcnow() - created_at
            if age > timedelta(days=30):
                audit_result["warnings"].append("Very old session - consider re-authentication")
                audit_result["risk_score"] += 20
        
        # Check last active time
        last_active = session_data.get("last_active")
        if last_active:
            inactive_duration = datetime.utcnow() - last_active
            if inactive_duration > timedelta(days=7):
                audit_result["warnings"].append("Session inactive for over 7 days")
                audit_result["risk_score"] += 15
        
        # Determine if suspicious
        audit_result["is_suspicious"] = audit_result["risk_score"] >= 30
        
        return audit_result
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token for form protection"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, stored_token: str) -> bool:
        """Verify CSRF token"""
        return secrets.compare_digest(token, stored_token)

# Create global instance
security_auditor = SecurityAuditor()
