"""
Kali (Security Enforcement) API Router

Provides API endpoints for security monitoring, threat detection,
and security policy enforcement.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from ..core.config import settings
from ..core.database import get_db
from ..core.monitoring import metrics

router = APIRouter()


class SecurityThreat(BaseModel):
    """Security threat detection"""
    threat_id: str
    severity: str
    threat_type: str
    source_ip: str
    target_resource: str
    description: str
    detected_at: str
    status: str


class VulnerabilityReport(BaseModel):
    """Vulnerability assessment report"""
    scan_id: str
    resource_id: str
    vulnerabilities_found: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    scan_date: str


class SecurityPolicyRequest(BaseModel):
    """Security policy request"""
    name: str = Field(..., description="Policy name")
    policy_type: str = Field(..., description="Type of security policy")
    rules: List[str] = Field(..., description="Security rules")
    enabled: bool = Field(default=True, description="Policy enabled status")


@router.get("/threats")
async def list_threats(
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    db=Depends(get_db)
):
    """List detected security threats"""
    
    if not settings.KALI_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Kali service is disabled"
        )
    
    try:
        # Mock data
        threats = [
            SecurityThreat(
                threat_id=str(uuid.uuid4()),
                severity="high",
                threat_type="brute_force",
                source_ip="192.168.1.100",
                target_resource="web-server-01",
                description="Multiple failed login attempts detected",
                detected_at=datetime.now(timezone.utc).isoformat(),
                status="active"
            )
        ]
        
        metrics.record_module_status("kali", True)
        
        return {"threats": threats, "total": len(threats)}
        
    except Exception as e:
        metrics.record_module_status("kali", False)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list threats: {str(e)}"
        )


@router.post("/scan/{resource_id}")
async def scan_vulnerabilities(resource_id: str, db=Depends(get_db)):
    """Perform vulnerability scan on resource"""
    
    try:
        scan_id = str(uuid.uuid4())
        
        # Mock vulnerability scan result
        report = VulnerabilityReport(
            scan_id=scan_id,
            resource_id=resource_id,
            vulnerabilities_found=5,
            critical_count=0,
            high_count=1,
            medium_count=2,
            low_count=2,
            scan_date=datetime.now(timezone.utc).isoformat()
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vulnerability scan failed: {str(e)}"
        )


@router.post("/policies")
async def create_security_policy(
    request: SecurityPolicyRequest, db=Depends(get_db)
):
    """Create new security policy"""
    
    try:
        policy_id = str(uuid.uuid4())
        
        return {
            "policy_id": policy_id,
            "name": request.name,
            "policy_type": request.policy_type,
            "enabled": request.enabled,
            "rules_count": len(request.rules),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Security policy creation failed: {str(e)}"
        )


@router.post("/block-ip")
async def block_ip_address(ip_address: str, reason: str, db=Depends(get_db)):
    """Block IP address for security reasons"""
    
    try:
        block_id = str(uuid.uuid4())
        
        return {
            "block_id": block_id,
            "ip_address": ip_address,
            "reason": reason,
            "status": "blocked",
            "blocked_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"IP blocking failed: {str(e)}"
        )


@router.get("/security-dashboard")
async def get_security_dashboard(db=Depends(get_db)):
    """Get security dashboard metrics"""
    
    try:
        dashboard = {
            "active_threats": 3,
            "blocked_ips": 15,
            "security_score": 87.5,
            "vulnerabilities": {
                "critical": 0,
                "high": 2,
                "medium": 8,
                "low": 12
            },
            "recent_scans": 5,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security dashboard: {str(e)}"
        )
