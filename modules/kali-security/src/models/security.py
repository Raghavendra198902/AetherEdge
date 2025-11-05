"""
Kali Security Engine - Data Models
Sacred protection and security threat management
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import ipaddress


class ThreatLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(str, Enum):
    INTRUSION_ATTEMPT = "intrusion_attempt"
    MALWARE_DETECTED = "malware_detected"
    POLICY_VIOLATION = "policy_violation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    COMPLIANCE_VIOLATION = "compliance_violation"
    NETWORK_ANOMALY = "network_anomaly"


class VulnerabilityStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED_RISK = "accepted_risk"
    FALSE_POSITIVE = "false_positive"


class ComplianceFramework(str, Enum):
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    NIST = "nist"
    CIS = "cis"
    OWASP = "owasp"


class SecurityPolicy(BaseModel):
    """Security policy definition and enforcement"""
    id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    
    # Policy details
    policy_type: str = Field(..., description="Type of security policy")
    severity: ThreatLevel = Field(..., description="Policy violation severity")
    framework: Optional[ComplianceFramework] = Field(None, description="Compliance framework")
    
    # Policy rules
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules and conditions")
    enforcement_mode: str = Field(..., description="Enforcement mode (monitor/enforce)")
    auto_remediation: bool = Field(default=False, description="Auto-remediation enabled")
    
    # Scope and targets
    target_resources: List[str] = Field(default_factory=list, description="Target resource types")
    target_environments: List[str] = Field(default_factory=list, description="Target environments")
    excluded_resources: List[str] = Field(default_factory=list, description="Excluded resources")
    
    # Metadata
    version: str = Field(..., description="Policy version")
    created_by: str = Field(..., description="Policy creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    enabled: bool = Field(default=True, description="Policy enabled status")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "policy_encryption_at_rest",
                "name": "Encryption at Rest Policy",
                "description": "Ensures all data is encrypted at rest",
                "policy_type": "data_protection",
                "severity": "high",
                "framework": "soc2",
                "rules": [
                    {
                        "condition": "resource_type == 'database'",
                        "requirement": "encryption_enabled == true"
                    }
                ],
                "enforcement_mode": "enforce",
                "auto_remediation": True,
                "version": "1.0.0",
                "created_by": "security_team"
            }
        }


class SecurityEvent(BaseModel):
    """Security event and incident tracking"""
    id: str = Field(..., description="Unique event identifier")
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Event description")
    
    # Event classification
    event_type: SecurityEventType = Field(..., description="Type of security event")
    threat_level: ThreatLevel = Field(..., description="Threat severity level")
    category: str = Field(..., description="Event category")
    subcategory: Optional[str] = Field(None, description="Event subcategory")
    
    # Source information
    source_ip: Optional[str] = Field(None, description="Source IP address")
    source_hostname: Optional[str] = Field(None, description="Source hostname")
    source_user: Optional[str] = Field(None, description="Source user")
    source_system: Optional[str] = Field(None, description="Source system")
    
    # Target information
    target_resource: Optional[str] = Field(None, description="Target resource")
    target_ip: Optional[str] = Field(None, description="Target IP address")
    target_port: Optional[int] = Field(None, description="Target port")
    target_service: Optional[str] = Field(None, description="Target service")
    
    # Event details
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    evidence: List[str] = Field(default_factory=list, description="Evidence URLs/paths")
    indicators: List[str] = Field(default_factory=list, description="Threat indicators")
    
    # Response and status
    status: str = Field(default="open", description="Event status")
    assigned_to: Optional[str] = Field(None, description="Assigned analyst")
    resolution: Optional[str] = Field(None, description="Resolution details")
    false_positive: bool = Field(default=False, description="Marked as false positive")
    
    # Temporal information
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    
    # Related events
    related_events: List[str] = Field(default_factory=list, description="Related event IDs")
    correlation_id: Optional[str] = Field(None, description="Correlation identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "event_unauthorized_access_001",
                "title": "Unauthorized SSH Access Attempt",
                "description": "Multiple failed SSH login attempts detected",
                "event_type": "unauthorized_access",
                "threat_level": "medium",
                "category": "authentication",
                "source_ip": "192.168.1.100",
                "target_resource": "web-server-01",
                "target_port": 22,
                "status": "open"
            }
        }


class Vulnerability(BaseModel):
    """Vulnerability assessment and tracking"""
    id: str = Field(..., description="Unique vulnerability identifier")
    cve_id: Optional[str] = Field(None, description="CVE identifier")
    title: str = Field(..., description="Vulnerability title")
    description: str = Field(..., description="Vulnerability description")
    
    # Vulnerability details
    severity: ThreatLevel = Field(..., description="Vulnerability severity")
    cvss_score: Optional[float] = Field(None, description="CVSS score")
    cvss_vector: Optional[str] = Field(None, description="CVSS vector")
    vulnerability_type: str = Field(..., description="Type of vulnerability")
    
    # Affected resources
    affected_resources: List[str] = Field(..., description="Affected resource IDs")
    affected_software: List[str] = Field(default_factory=list, description="Affected software")
    affected_versions: List[str] = Field(default_factory=list, description="Affected versions")
    
    # Status and remediation
    status: VulnerabilityStatus = Field(default=VulnerabilityStatus.OPEN)
    remediation_steps: List[str] = Field(default_factory=list, description="Remediation steps")
    mitigation_measures: List[str] = Field(default_factory=list, description="Mitigation measures")
    patch_available: bool = Field(default=False, description="Patch available")
    patch_url: Optional[str] = Field(None, description="Patch download URL")
    
    # Discovery and tracking
    discovered_by: str = Field(..., description="Discovery source")
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_verified: datetime = Field(default_factory=datetime.utcnow)
    
    # Risk assessment
    exploitability: str = Field(..., description="Exploitability level")
    business_impact: str = Field(..., description="Business impact assessment")
    risk_score: float = Field(..., description="Overall risk score")
    
    # References and links
    references: List[str] = Field(default_factory=list, description="Reference URLs")
    vendor_advisory: Optional[str] = Field(None, description="Vendor advisory URL")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "vuln_cve_2024_001",
                "cve_id": "CVE-2024-001",
                "title": "Remote Code Execution in Web Server",
                "description": "Buffer overflow vulnerability allows RCE",
                "severity": "critical",
                "cvss_score": 9.8,
                "vulnerability_type": "buffer_overflow",
                "affected_resources": ["web-server-01", "web-server-02"],
                "status": "open",
                "exploitability": "high",
                "business_impact": "critical",
                "risk_score": 9.5,
                "discovered_by": "vulnerability_scanner"
            }
        }


class ThreatIntelligence(BaseModel):
    """Threat intelligence data and indicators"""
    id: str = Field(..., description="Unique intelligence identifier")
    title: str = Field(..., description="Intelligence title")
    description: str = Field(..., description="Intelligence description")
    
    # Threat classification
    threat_type: str = Field(..., description="Type of threat")
    threat_actor: Optional[str] = Field(None, description="Threat actor/group")
    campaign: Optional[str] = Field(None, description="Campaign name")
    threat_level: ThreatLevel = Field(..., description="Threat level")
    
    # Indicators of Compromise (IOCs)
    iocs: List[Dict[str, str]] = Field(default_factory=list, description="IOCs")
    ip_addresses: List[str] = Field(default_factory=list, description="Malicious IPs")
    domains: List[str] = Field(default_factory=list, description="Malicious domains")
    file_hashes: List[str] = Field(default_factory=list, description="Malicious file hashes")
    urls: List[str] = Field(default_factory=list, description="Malicious URLs")
    
    # Context and analysis
    tactics: List[str] = Field(default_factory=list, description="MITRE ATT&CK tactics")
    techniques: List[str] = Field(default_factory=list, description="MITRE ATT&CK techniques")
    malware_families: List[str] = Field(default_factory=list, description="Malware families")
    attack_patterns: List[str] = Field(default_factory=list, description="Attack patterns")
    
    # Source and confidence
    source: str = Field(..., description="Intelligence source")
    confidence: float = Field(..., description="Confidence score (0-1)")
    reliability: str = Field(..., description="Source reliability")
    tlp_marking: str = Field(default="WHITE", description="TLP marking")
    
    # Temporal information
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Intelligence expiration")
    
    # Related intelligence
    related_intelligence: List[str] = Field(default_factory=list, description="Related intel IDs")
    tags: List[str] = Field(default_factory=list, description="Intelligence tags")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "intel_apt_campaign_001",
                "title": "APT Group Targeting Infrastructure",
                "description": "Advanced persistent threat targeting cloud infrastructure",
                "threat_type": "apt",
                "threat_actor": "APT-X",
                "threat_level": "high",
                "iocs": [
                    {"type": "ip", "value": "1.2.3.4", "description": "C2 server"}
                ],
                "tactics": ["initial_access", "persistence"],
                "techniques": ["T1190", "T1078"],
                "source": "threat_intel_feed",
                "confidence": 0.9,
                "reliability": "high"
            }
        }


class ComplianceRule(BaseModel):
    """Compliance rule and assessment"""
    id: str = Field(..., description="Unique rule identifier")
    rule_id: str = Field(..., description="Standard rule ID")
    title: str = Field(..., description="Rule title")
    description: str = Field(..., description="Rule description")
    
    # Compliance framework
    framework: ComplianceFramework = Field(..., description="Compliance framework")
    section: str = Field(..., description="Framework section")
    control_id: str = Field(..., description="Control identifier")
    
    # Rule definition
    rule_type: str = Field(..., description="Type of rule")
    assessment_criteria: str = Field(..., description="Assessment criteria")
    evidence_required: List[str] = Field(default_factory=list, description="Required evidence")
    automated_check: bool = Field(default=False, description="Automated check available")
    
    # Assessment results
    status: str = Field(default="not_assessed", description="Compliance status")
    last_assessment: Optional[datetime] = Field(None, description="Last assessment date")
    next_assessment: Optional[datetime] = Field(None, description="Next assessment date")
    assessment_frequency: str = Field(..., description="Assessment frequency")
    
    # Non-compliance handling
    remediation_steps: List[str] = Field(default_factory=list, description="Remediation steps")
    responsible_party: str = Field(..., description="Responsible party")
    risk_rating: ThreatLevel = Field(..., description="Non-compliance risk")
    
    # References
    references: List[str] = Field(default_factory=list, description="Reference documents")
    related_controls: List[str] = Field(default_factory=list, description="Related controls")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "rule_soc2_cc6_1",
                "rule_id": "CC6.1",
                "title": "Logical Access Security",
                "description": "Entity implements controls for logical access security",
                "framework": "soc2",
                "section": "Common Criteria",
                "control_id": "CC6.1",
                "rule_type": "security_control",
                "assessment_criteria": "Access controls implemented and effective",
                "automated_check": True,
                "assessment_frequency": "quarterly",
                "responsible_party": "security_team",
                "risk_rating": "high"
            }
        }


class SecurityScan(BaseModel):
    """Security scan configuration and results"""
    id: str = Field(..., description="Unique scan identifier")
    name: str = Field(..., description="Scan name")
    description: str = Field(..., description="Scan description")
    
    # Scan configuration
    scan_type: str = Field(..., description="Type of scan")
    scanner: str = Field(..., description="Scanner used")
    targets: List[str] = Field(..., description="Scan targets")
    scan_profile: str = Field(..., description="Scan profile/template")
    
    # Schedule and execution
    scheduled: bool = Field(default=False, description="Scheduled scan")
    schedule_expression: Optional[str] = Field(None, description="Cron expression")
    last_run: Optional[datetime] = Field(None, description="Last run timestamp")
    next_run: Optional[datetime] = Field(None, description="Next run timestamp")
    
    # Results and findings
    status: str = Field(default="pending", description="Scan status")
    total_findings: int = Field(default=0, description="Total findings count")
    critical_findings: int = Field(default=0, description="Critical findings")
    high_findings: int = Field(default=0, description="High severity findings")
    medium_findings: int = Field(default=0, description="Medium severity findings")
    low_findings: int = Field(default=0, description="Low severity findings")
    
    # Scan artifacts
    results_url: Optional[str] = Field(None, description="Results file URL")
    report_url: Optional[str] = Field(None, description="Report URL")
    raw_output: Optional[str] = Field(None, description="Raw scanner output")
    
    # Metadata
    created_by: str = Field(..., description="Scan creator")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    duration: Optional[int] = Field(None, description="Scan duration in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "scan_weekly_vulnerability",
                "name": "Weekly Vulnerability Scan",
                "description": "Automated weekly vulnerability assessment",
                "scan_type": "vulnerability",
                "scanner": "nessus",
                "targets": ["10.0.0.0/24"],
                "scan_profile": "full_scan",
                "scheduled": True,
                "schedule_expression": "0 2 * * 1",
                "status": "completed",
                "total_findings": 15,
                "critical_findings": 2,
                "high_findings": 5,
                "created_by": "security_automation"
            }
        }
