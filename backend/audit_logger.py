"""
019Solutions - Audit Logging System
Enterprise-grade activity tracking and security monitoring
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import json
from pathlib import Path

# Setup audit logger
audit_log_path = Path(__file__).parent / "logs" / "audit.log"
audit_log_path.parent.mkdir(exist_ok=True)

# Create audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# File handler for audit logs
audit_handler = logging.FileHandler(audit_log_path)
audit_handler.setLevel(logging.INFO)

# Formatter
audit_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)

# Console handler (optional)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(audit_formatter)
audit_logger.addHandler(console_handler)

class AuditLog:
    """Centralized audit logging"""
    
    @staticmethod
    def log_event(
        event_type: str,
        user: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        status: str = "success",
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log audit event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user": user or "anonymous",
            "action": action,
            "resource": resource,
            "status": status,
            "ip_address": ip_address,
            "details": details or {}
        }
        
        audit_logger.info(json.dumps(log_entry))
    
    @staticmethod
    def log_auth_attempt(username: str, success: bool, ip_address: str, reason: Optional[str] = None):
        """Log authentication attempt"""
        AuditLog.log_event(
            event_type="authentication",
            user=username,
            action="login",
            status="success" if success else "failed",
            ip_address=ip_address,
            details={"reason": reason} if reason else None
        )
    
    @staticmethod
    def log_admin_action(admin: str, action: str, resource: str, ip_address: str, details: Optional[Dict] = None):
        """Log admin panel action"""
        AuditLog.log_event(
            event_type="admin_action",
            user=admin,
            action=action,
            resource=resource,
            status="success",
            ip_address=ip_address,
            details=details
        )
    
    @staticmethod
    def log_api_access(endpoint: str, method: str, user: Optional[str], ip_address: str, status_code: int):
        """Log API access"""
        AuditLog.log_event(
            event_type="api_access",
            user=user,
            action=method,
            resource=endpoint,
            status="success" if status_code < 400 else "failed",
            ip_address=ip_address,
            details={"status_code": status_code}
        )
    
    @staticmethod
    def log_security_event(event: str, severity: str, ip_address: str, details: Optional[Dict] = None):
        """Log security-related event"""
        AuditLog.log_event(
            event_type="security",
            action=event,
            status=severity,
            ip_address=ip_address,
            details=details
        )
    
    @staticmethod
    def log_data_change(user: str, resource: str, action: str, ip_address: str, old_value: Any = None, new_value: Any = None):
        """Log data modification"""
        AuditLog.log_event(
            event_type="data_change",
            user=user,
            action=action,
            resource=resource,
            status="success",
            ip_address=ip_address,
            details={
                "old_value": str(old_value) if old_value else None,
                "new_value": str(new_value) if new_value else None
            }
        )

# Export singleton
audit_log = AuditLog()
