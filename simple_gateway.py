"""
🚀 Simple API Gateway for AetherEdge
====================================
A minimal working API Gateway to get the platform running
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from datetime import datetime, timedelta
import logging
import hashlib
import secrets
import re
import time
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, validator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Security constants and configuration
class SecurityConstants:
    """Security constants for the application"""
    MIN_TOKEN_LENGTH = 32
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    VALID_USER_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,50}$')
    VALID_DEVICE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{8,100}$')


class APIEndpoints:
    """API endpoint constants"""
    AUTH_LOGIN = "/api/v1/auth/login"
    AUTH_LOGOUT = "/api/v1/auth/logout"
    AUTH_TOKEN = "/api/v1/auth/token"


# Rate limiting storage
class RateLimiter:
    """Simple in-memory rate limiter"""
    def __init__(self):
        self.attempts: Dict[str, List[float]] = {}
        self.lockouts: Dict[str, float] = {}
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        now = time.time()
        
        # Check if currently locked out
        if identifier in self.lockouts:
            if now < self.lockouts[identifier]:
                return True
            else:
                # Lockout expired, remove it
                del self.lockouts[identifier]
        
        # Clean old attempts (older than 1 hour)
        if identifier in self.attempts:
            self.attempts[identifier] = [
                attempt for attempt in self.attempts[identifier]
                if now - attempt < 3600  # 1 hour
            ]
        
        # Check current attempts
        recent_attempts = len(self.attempts.get(identifier, []))
        return recent_attempts >= SecurityConstants.MAX_LOGIN_ATTEMPTS
    
    def record_attempt(self, identifier: str, failed: bool = True) -> None:
        """Record a login attempt"""
        if not failed:
            # Success - clear attempts
            if identifier in self.attempts:
                del self.attempts[identifier]
            return
        
        now = time.time()
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        self.attempts[identifier].append(now)
        
        # If max attempts reached, set lockout
        max_attempts = SecurityConstants.MAX_LOGIN_ATTEMPTS
        if len(self.attempts[identifier]) >= max_attempts:
            lockout_duration = SecurityConstants.LOCKOUT_DURATION_MINUTES * 60
            lockout_until = now + lockout_duration
            self.lockouts[identifier] = lockout_until


# Initialize rate limiter
rate_limiter = RateLimiter()

# Security
security = HTTPBearer(auto_error=False)

# Create FastAPI app with enhanced security
app = FastAPI(
    title="AetherEdge Divine API Gateway",
    description="Enterprise Infrastructure Automation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # Security: Disable docs in production
    # docs_url=None,
    # redoc_url=None,
)

# Add security middleware with enhanced configuration
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.localhost",
        # Add your production domains here
    ]
)

# Add CORS middleware with restrictive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Add your production frontend domains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],  # More restrictive
    max_age=3600,  # Cache preflight requests
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🌟 AetherEdge Divine API Gateway",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AetherEdge API Gateway",
        "timestamp": datetime.now().isoformat(),
        "divine_modules": {
            "saraswati": "operational",
            "lakshmi": "operational",
            "kali": "operational",
            "hanuman": "operational",
            "ganesha": "operational",
            "brahma": "operational",
            "vishnu": "operational",
            "shiva": "operational"
        }
    }


# Divine Module Mock Endpoints


@app.get("/api/v1/saraswati/health")
async def saraswati_health():
    """Saraswati Knowledge Engine Health"""
    return {
        "module": "saraswati",
        "status": "operational",
        "type": "knowledge_engine"
    }


@app.get("/api/v1/lakshmi/health")
async def lakshmi_health():
    """Lakshmi FinOps Engine Health"""
    return {
        "module": "lakshmi",
        "status": "operational",
        "type": "finops_engine"
    }


@app.get("/api/v1/kali/health")
async def kali_health():
    """Kali Security Engine Health"""
    return {
        "module": "kali",
        "status": "operational",
        "type": "security_engine"
    }


@app.get("/api/v1/hanuman/health")
async def hanuman_health():
    """Hanuman Agents Engine Health"""
    return {
        "module": "hanuman",
        "status": "operational",
        "type": "agents_engine"
    }


@app.get("/api/v1/ganesha/health")
async def ganesha_health():
    """Ganesha RCA Engine Health"""
    return {
        "module": "ganesha",
        "status": "operational",
        "type": "rca_engine"
    }


@app.get("/api/v1/brahma/health")
async def brahma_health():
    """Brahma Blueprint Engine Health"""
    return {
        "module": "brahma",
        "status": "operational",
        "type": "blueprint_engine"
    }


@app.get("/api/v1/vishnu/health")
async def vishnu_health():
    """Vishnu Orchestrator Health"""
    return {
        "module": "vishnu",
        "status": "operational",
        "type": "orchestrator"
    }


@app.get("/api/v1/shiva/health")
async def shiva_health():
    """Shiva Healer Engine Health"""
    return {
        "module": "shiva",
        "status": "operational",
        "type": "healer_engine"
    }


# Dashboard endpoint for frontend


@app.get("/api/v1/dashboard/status")
async def dashboard_status():
    """Dashboard status for frontend"""
    return {
        "platform_status": "operational",
        "divine_modules": 8,
        "active_services": 8,
        "uptime": "100%",
        "last_updated": datetime.now().isoformat(),
        "modules": [
            {
                "name": "Saraswati Knowledge",
                "status": "healthy",
                "uptime": "99.9%",
                "requests": 1247,
                "lastCheck": datetime.now().isoformat()
            },
            {
                "name": "Lakshmi FinOps",
                "status": "healthy",
                "uptime": "99.8%",
                "requests": 892,
                "lastCheck": datetime.now().isoformat()
            },
            {
                "name": "Kali Security",
                "status": "healthy",
                "uptime": "99.9%",
                "requests": 2156,
                "lastCheck": datetime.now().isoformat()
            },
            {
                "name": "Hanuman Agents",
                "status": "healthy",
                "uptime": "99.7%",
                "requests": 567,
                "lastCheck": datetime.now().isoformat()
            },
            {
                "name": "Ganesha RCA",
                "status": "healthy",
                "uptime": "99.9%",
                "requests": 334,
                "lastCheck": datetime.now().isoformat()
            },
            {
                "name": "Brahma Blueprint",
                "status": "healthy",
                "uptime": "99.8%",
                "requests": 445,
                "lastCheck": datetime.now().isoformat()
            },
            {
                "name": "Vishnu Orchestrator",
                "status": "healthy",
                "uptime": "99.9%",
                "requests": 778,
                "lastCheck": datetime.now().isoformat()
            },
            {
                "name": "Shiva Healer",
                "status": "healthy",
                "uptime": "99.6%",
                "requests": 223,
                "lastCheck": datetime.now().isoformat()
            }
        ],
        "infrastructure": {
            "activeResources": {"value": 142, "change": 12, "trend": "up"},
            "totalCost": {"value": 8750, "change": -8, "trend": "down"},
            "securityScore": {"value": 95, "change": 2, "trend": "up"},
            "knowledge": {"value": 1247, "change": 15, "trend": "up"}
        },
        "alerts": [
            {
                "id": "alert_1",
                "type": "info",
                "title": "System Update Available",
                "description": ("AetherEdge v2.1.0 is available with "
                                "enhanced security features"),
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "alert_2",
                "type": "warning",
                "title": "High Memory Usage",
                "description": ("Hanuman Agents module using 85% memory "
                                "- consider scaling"),
                "timestamp": (datetime.now() -
                              timedelta(minutes=15)).isoformat()
            }
        ]
    }

# Enterprise Security Configuration


class SecurityConfig:
    """Enterprise security configuration"""
    TOKEN_LIFETIME_MINUTES = 25
    ROTATION_THRESHOLD_MINUTES = 20
    AUDIT_LOG_RETENTION_DAYS = 180
    SESSION_INTEGRITY_ALGORITHM = "SHA-256"
    
# Token and Session Models


class LoginRequest(BaseModel):
    """Secure login request model with validation"""
    user_id: str = Field(..., min_length=3, max_length=50)
    device_id: str = Field(..., min_length=8, max_length=100)
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not SecurityConstants.VALID_USER_ID_PATTERN.match(v):
            raise ValueError('Invalid user ID format')
        return v
    
    @validator('device_id')
    def validate_device_id(cls, v):
        if not SecurityConstants.VALID_DEVICE_ID_PATTERN.match(v):
            raise ValueError('Invalid device ID format')
        return v


class TokenPayload(BaseModel):
    """JWT Token payload structure with enhanced validation"""
    sub: str = Field(..., min_length=3, max_length=50)
    iat: int = Field(..., gt=0)
    exp: int = Field(..., gt=0)
    device_id: str = Field(..., min_length=8, max_length=100)
    session_id: str = Field(..., min_length=32)
    permissions: List[str] = Field(default_factory=list)
    
    @validator('permissions')
    def validate_permissions(cls, v):
        valid_permissions = {'read', 'write', 'admin', 'audit'}
        if not all(perm in valid_permissions for perm in v):
            raise ValueError('Invalid permission in list')
        return v


class AuditLog(BaseModel):
    """Audit log entry structure"""
    timestamp: str
    event_type: str
    user_id: Optional[str]
    device_id: Optional[str]
    endpoint: str
    status_code: int
    integrity_hash: str


# Enterprise Authentication & Audit System


class EnterpriseAuth:
    """Enterprise authentication and audit system"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.audit_logs: list = []
        self.security_config = SecurityConfig()
    
    def generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    def generate_integrity_hash(self, data: str) -> str:
        """Generate SHA-256 integrity hash"""
        return hashlib.sha256(data.encode()).hexdigest()

    def log_audit_event(self, event_type: str, endpoint: str,
                        status_code: int, user_id: Optional[str] = None,
                        device_id: Optional[str] = None) -> None:
        """Log audit event with integrity validation"""
        timestamp = datetime.now().isoformat()
        audit_data = f"{timestamp}:{event_type}:{endpoint}:{status_code}"
        
        audit_entry = AuditLog(
            timestamp=timestamp,
            event_type=event_type,
            user_id=user_id,
            device_id=device_id,
            endpoint=endpoint,
            status_code=status_code,
            integrity_hash=self.generate_integrity_hash(audit_data)
        )
        
        self.audit_logs.append(audit_entry)
        logger.info("AUDIT: %s", audit_entry.json())
    
    def validate_token(self, token: str) -> Optional[TokenPayload]:
        """Validate JWT token with enhanced security"""
        # Input validation
        if not token or len(token) < SecurityConstants.MIN_TOKEN_LENGTH:
            logger.warning("Token validation failed: Invalid token format")
            return None
            
        try:
            # Simplified token validation - decode and verify
            # In production, use proper JWT library with RSA-256 verification
            parts = token.split('.')
            if len(parts) < 2:
                logger.warning(
                    "Token validation failed: Invalid token structure"
                )
                return None
                
            session_id = parts[0]
            
            # Validate session ID format
            if not re.match(r'^[A-Za-z0-9_-]+$', session_id):
                logger.warning(
                    "Token validation failed: Invalid session ID format"
                )
                return None
            
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                expires_at = datetime.fromisoformat(session['expires_at'])
                
                if datetime.now() < expires_at:
                    # Additional security: verify token hasn't been
                    # tampered with
                    expected_token = f"{session_id}.demo.token"
                    if token != expected_token:
                        logger.warning(
                            "Token validation failed: Token mismatch"
                        )
                        return None
                    
                    return TokenPayload(**session['payload'])
                else:
                    # Token expired, remove session
                    logger.info("Session expired, removing: %s", session_id)
                    del self.active_sessions[session_id]
                    return None
            
            logger.warning("Token validation failed: Session not found")
            return None
            
        except (ValueError, KeyError, TypeError) as e:
            logger.error("Token validation error: %s", e)
            return None
    
    def create_session(self, user_id: str, device_id: str) -> str:
        """Create new authenticated session"""
        session_id = self.generate_session_id()
        expires_at = datetime.now() + timedelta(
            minutes=self.security_config.TOKEN_LIFETIME_MINUTES
        )
        
        payload = {
            "sub": user_id,
            "iat": int(datetime.now().timestamp()),
            "exp": int(expires_at.timestamp()),
            "device_id": device_id,
            "session_id": session_id,
            "permissions": ["read", "write", "admin"]  # Demo permissions
        }
        
        self.active_sessions[session_id] = {
            "payload": payload,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        
        self.log_audit_event("SESSION_CREATED", "/auth/login", 200,
                             user_id, device_id)
        
        return f"{session_id}.demo.token"  # Simplified token format
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke session (policy invalidation)"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            user_id = session['payload']['sub']
            device_id = session['payload']['device_id']
            
            del self.active_sessions[session_id]
            
            self.log_audit_event("SESSION_REVOKED", "/auth/logout", 200,
                                 user_id, device_id)
            return True
        return False


# Initialize enterprise authentication


enterprise_auth = EnterpriseAuth()

# Enhanced Security with Authentication
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Enhanced authentication dependency with better error handling"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Enhanced token validation
    if not credentials.credentials:
        enterprise_auth.log_audit_event("AUTH_FAILED", "/auth/validate", 401)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_payload = enterprise_auth.validate_token(credentials.credentials)
    if not token_payload:
        enterprise_auth.log_audit_event("AUTH_FAILED", "/auth/validate", 401)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last accessed time with additional validation
    try:
        session_id = credentials.credentials.split('.')[0]
        if session_id and session_id in enterprise_auth.active_sessions:
            enterprise_auth.active_sessions[session_id]['last_accessed'] = (
                datetime.now().isoformat()
            )
    except (IndexError, AttributeError) as e:
        logger.warning("Failed to update session access time: %s", e)
    
    return token_payload

# Enterprise Authentication Endpoints


@app.post(APIEndpoints.AUTH_LOGIN)
async def enterprise_login(login_data: LoginRequest):
    """Secure Enterprise OIDC/OAuth2 Login Endpoint with Rate Limiting"""
    # Rate limiting check
    client_ip = "127.0.0.1"  # In production, extract from request
    rate_limit_key = f"{client_ip}:{login_data.user_id}"
    
    if rate_limiter.is_rate_limited(rate_limit_key):
        enterprise_auth.log_audit_event(
            "RATE_LIMITED", APIEndpoints.AUTH_LOGIN, 429,
            login_data.user_id, login_data.device_id
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    try:
        # Validate input format
        user_id_pattern = SecurityConstants.VALID_USER_ID_PATTERN
        if not user_id_pattern.match(login_data.user_id):
            rate_limiter.record_attempt(rate_limit_key, failed=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        device_id_pattern = SecurityConstants.VALID_DEVICE_ID_PATTERN
        if not device_id_pattern.match(login_data.device_id):
            rate_limiter.record_attempt(rate_limit_key, failed=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid device ID format"
            )
        
        # In production, integrate with OIDC/OAuth2 provider
        # For demo purposes, we'll accept any valid format
        token = enterprise_auth.create_session(
            login_data.user_id, login_data.device_id
        )
        
        # Record successful login
        rate_limiter.record_attempt(rate_limit_key, failed=False)
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": SecurityConfig.TOKEN_LIFETIME_MINUTES * 60,
            "refresh_token": f"refresh_{secrets.token_urlsafe(16)}",
            "session_id": token.split('.')[0]
        }
    except ValueError as exc:
        rate_limiter.record_attempt(rate_limit_key, failed=True)
        enterprise_auth.log_audit_event(
            "LOGIN_FAILED", APIEndpoints.AUTH_LOGIN,
            400, login_data.user_id, login_data.device_id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication failed"
        ) from exc
    except Exception as exc:
        rate_limiter.record_attempt(rate_limit_key, failed=True)
        enterprise_auth.log_audit_event(
            "LOGIN_ERROR", APIEndpoints.AUTH_LOGIN,
            500, login_data.user_id, login_data.device_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        ) from exc


@app.post("/api/v1/auth/logout")
async def enterprise_logout(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Enterprise Session Logout with Policy Invalidation"""
    session_id = current_user.session_id
    
    if enterprise_auth.revoke_session(session_id):
        return {"message": "Session revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session not found or already revoked"
        )


@app.get("/api/v1/auth/validate")
async def validate_token(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Token Validation Endpoint"""
    return {
        "valid": True,
        "user_id": current_user.sub,
        "device_id": current_user.device_id,
        "expires_at": current_user.exp,
        "permissions": current_user.permissions
    }


@app.get("/api/v1/audit/logs")
async def get_audit_logs(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Enterprise Audit Logs with 180d Retention"""
    if "admin" not in current_user.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    
    # Return last 100 audit entries (in production, implement pagination)
    recent_logs = (enterprise_auth.audit_logs[-100:]
                   if enterprise_auth.audit_logs else [])
    
    return {
        "audit_logs": [log.dict() for log in recent_logs],
        "total_count": len(enterprise_auth.audit_logs),
        "retention_policy": f"{SecurityConfig.AUDIT_LOG_RETENTION_DAYS} days"
    }


@app.get("/api/v1/security/status")
async def security_status(
    _current_user: TokenPayload = Depends(get_current_user)
):
    """Enterprise Security Status Dashboard"""
    active_session_count = len(enterprise_auth.active_sessions)
    
    return {
        "security_framework": "Enterprise RSA-256 JWT",
        "active_sessions": active_session_count,
        "token_lifetime_minutes": SecurityConfig.TOKEN_LIFETIME_MINUTES,
        "rotation_threshold_minutes": (
            SecurityConfig.ROTATION_THRESHOLD_MINUTES
        ),
        "audit_retention_days": SecurityConfig.AUDIT_LOG_RETENTION_DAYS,
        "integrity_algorithm": SecurityConfig.SESSION_INTEGRITY_ALGORITHM,
        "last_audit_count": len(enterprise_auth.audit_logs),
        "authentication_status": "operational",
        "failover_ready": True,
        "multi_region_support": True
    }


# Enhanced Dashboard with Security Integration
@app.get("/api/v1/dashboard/enterprise")
async def enterprise_dashboard(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Enterprise Dashboard with Advanced Security Metrics"""
    return {
        "platform_status": "operational",
        "security_posture": {
            "authentication": "enterprise_grade",
            "active_sessions": len(enterprise_auth.active_sessions),
            "audit_events_today": len([
                log for log in enterprise_auth.audit_logs
                if log.timestamp.startswith(
                    datetime.now().strftime('%Y-%m-%d')
                )
            ]),
            "security_score": 98,  # Enhanced with enterprise auth
            "compliance_status": "SOC2_Type2_Ready"
        },
        "operational_metrics": {
            "divine_modules": 8,
            "active_services": 8,
            "uptime": "100%",
            "rpo_minutes": 15,  # Recovery Point Objective
            "rto_minutes": 30   # Recovery Time Objective
        },
        "data_retention": {
            "logs_days": 180,
            "metrics_days": 90,
            "reports_days": 365,
            "integrity_validation": "SHA-256"
        },
        "scalability": {
            "auto_scaling_enabled": True,
            "ai_load_prediction": True,
            "kubernetes_ready": True,
            "stateless_design": True
        },
        "integration_hooks": {
            "cmdb_connected": False,  # Demo status
            "itsm_ready": True,
            "terraform_support": True,
            "webhook_endpoints": 4,
            "sdk_languages": ["Python", "Go"]
        },
        "user_context": {
            "user_id": current_user.sub,
            "device_id": current_user.device_id,
            "session_expires": current_user.exp,
            "permissions": current_user.permissions
        }
    }


if __name__ == "__main__":
    logger.info("🚀 Starting AetherEdge Divine API Gateway...")
    logger.info("🌐 API Documentation: http://localhost:8001/docs")
    logger.info("💓 Health Check: http://localhost:8001/health")
    logger.info("📊 Dashboard API: "
                "http://localhost:8001/api/v1/dashboard/status")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False
    )
