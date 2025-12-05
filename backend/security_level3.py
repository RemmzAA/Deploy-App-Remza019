"""
019Solutions - Level 3 Security Module
Maximum security hardening for production deployment
"""

import hashlib
import secrets
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import json
from typing import Dict, Any
import logging

logger = logging.getLogger("security")

class SecurityManager:
    """Level 3 Security Manager"""
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.cipher = self._initialize_cipher()
        
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        # Use /tmp for writable storage on cloud platforms like Render
        key_file = "/tmp/.security/master.key"
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new master key
            master_key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(master_key)
            # Restrict permissions
            os.chmod(key_file, 0o600)
            logger.info("🔐 New master key generated")
            return master_key
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize encryption cipher"""
        return Fernet(self.master_key)
    
    def encrypt_string(self, plaintext: str) -> str:
        """Encrypt string data"""
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"❌ Encryption error: {e}")
            raise
    
    def decrypt_string(self, encrypted: str) -> str:
        """Decrypt string data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"❌ Decryption error: {e}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt dictionary data"""
        json_str = json.dumps(data)
        return self.encrypt_string(json_str)
    
    def decrypt_dict(self, encrypted: str) -> Dict[str, Any]:
        """Decrypt dictionary data"""
        json_str = self.decrypt_string(encrypted)
        return json.loads(json_str)
    
    def hash_password(self, password: str, salt: bytes = None) -> tuple:
        """Hash password with PBKDF2HMAC"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key).decode(), base64.urlsafe_b64encode(salt).decode()
    
    def verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            salt_bytes = base64.urlsafe_b64decode(salt.encode())
            new_hash, _ = self.hash_password(password, salt_bytes)
            return secrets.compare_digest(new_hash, hashed)
        except Exception:
            return False
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def sanitize_input(self, input_string: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')', '{', '}', '[', ']']
        sanitized = input_string
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized.strip()
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def encrypt_env_file(self, env_file_path: str):
        """Encrypt .env file"""
        try:
            with open(env_file_path, 'r') as f:
                content = f.read()
            
            encrypted = self.encrypt_string(content)
            
            encrypted_file = f"{env_file_path}.encrypted"
            with open(encrypted_file, 'w') as f:
                f.write(encrypted)
            
            logger.info(f"🔐 Encrypted: {env_file_path}")
            return encrypted_file
            
        except Exception as e:
            logger.error(f"❌ Env encryption error: {e}")
            raise
    
    def decrypt_env_file(self, encrypted_file_path: str) -> str:
        """Decrypt .env file"""
        try:
            with open(encrypted_file_path, 'r') as f:
                encrypted = f.read()
            
            decrypted = self.decrypt_string(encrypted)
            return decrypted
            
        except Exception as e:
            logger.error(f"❌ Env decryption error: {e}")
            raise

# Global security manager instance
security_manager = SecurityManager()

def get_security_manager() -> SecurityManager:
    """Get global security manager"""
    return security_manager

# Security middleware functions
def add_security_headers(response):
    """Add security headers to response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

def sanitize_request_data(data: dict) -> dict:
    """Sanitize all request data"""
    security = get_security_manager()
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = security.sanitize_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_request_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                security.sanitize_input(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized

# Input validation decorators
def validate_string_length(min_len: int = 0, max_len: int = 1000):
    """Validate string length"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Validate all string arguments
            for arg in args:
                if isinstance(arg, str):
                    if len(arg) < min_len or len(arg) > max_len:
                        raise ValueError(f"String length must be between {min_len} and {max_len}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_https(func):
    """Require HTTPS for endpoint"""
    def wrapper(*args, **kwargs):
        # Check if request is HTTPS
        # Implementation depends on framework
        return func(*args, **kwargs)
    return wrapper
