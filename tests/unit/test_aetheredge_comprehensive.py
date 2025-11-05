"""
AetherEdge Platform - Comprehensive Test Suite
Unit tests for all core modules and components
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Import AetherEdge modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.api.main import app
from src.modules.brahma.blueprint_engine import BlueprintEngine
from src.modules.vishnu.orchestration_engine import OrchestrationEngine
from src.modules.shiva.healing_engine import HealingEngine
from src.modules.lakshmi.finops_engine import FinOpsEngine
from src.modules.kali.security_engine import SecurityEngine
from mlops.mlflow_manager import MLflowModelManager, AnomalyDetectionModel


class TestAetherEdgeAPI:
    """Test suite for FastAPI endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client fixture"""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "content-type" in response.headers
    
    def test_openapi_docs(self, client):
        """Test OpenAPI documentation"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_brahma_blueprint_generation(self, client):
        """Test Brahma blueprint generation endpoint"""
        payload = {
            "infrastructure_type": "kubernetes",
            "requirements": {
                "cpu": "4 cores",
                "memory": "8GB",
                "storage": "100GB"
            },
            "cloud_provider": "aws"
        }
        response = client.post("/api/v1/brahma/generate-blueprint", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "blueprint" in data
        assert "cost_estimate" in data
    
    def test_vishnu_policy_validation(self, client):
        """Test Vishnu policy validation endpoint"""
        payload = {
            "policy_type": "security",
            "rules": [
                {"condition": "cpu_usage > 80", "action": "scale_up"},
                {"condition": "memory_usage > 90", "action": "alert"}
            ]
        }
        response = client.post("/api/v1/vishnu/validate-policy", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "validation_result" in data
        assert "compliance_score" in data
    
    def test_shiva_healing_trigger(self, client):
        """Test Shiva healing trigger endpoint"""
        payload = {
            "incident_type": "service_down",
            "affected_services": ["api", "database"],
            "severity": "high"
        }
        response = client.post("/api/v1/shiva/trigger-healing", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "healing_plan" in data
        assert "estimated_time" in data
    
    def test_lakshmi_cost_analysis(self, client):
        """Test Lakshmi cost analysis endpoint"""
        payload = {
            "time_range": "30d",
            "services": ["api", "database", "monitoring"],
            "cloud_provider": "aws"
        }
        response = client.post("/api/v1/lakshmi/analyze-costs", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "cost_breakdown" in data
        assert "optimization_suggestions" in data
    
    def test_kali_security_scan(self, client):
        """Test Kali security scan endpoint"""
        payload = {
            "scan_type": "vulnerability",
            "targets": ["10.0.1.0/24"],
            "scan_level": "comprehensive"
        }
        response = client.post("/api/v1/kali/security-scan", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "scan_results" in data
        assert "vulnerabilities" in data


class TestBrahmaEngine:
    """Test suite for Brahma Blueprint Engine"""
    
    @pytest.fixture
    def engine(self):
        """Brahma engine fixture"""
        return BlueprintEngine()
    
    def test_generate_kubernetes_blueprint(self, engine):
        """Test Kubernetes blueprint generation"""
        requirements = {
            "infrastructure_type": "kubernetes",
            "services": ["api", "database", "cache"],
            "replicas": 3,
            "resources": {
                "cpu": "500m",
                "memory": "1Gi"
            }
        }
        
        blueprint = engine.generate_blueprint(requirements)
        
        assert blueprint is not None
        assert "apiVersion" in blueprint
        assert "kind" in blueprint
        assert blueprint["kind"] == "Deployment"
    
    def test_cost_estimation(self, engine):
        """Test cost estimation"""
        requirements = {
            "cloud_provider": "aws",
            "instance_type": "t3.medium",
            "instances": 3,
            "storage_gb": 100
        }
        
        cost = engine.estimate_costs(requirements)
        
        assert cost > 0
        assert isinstance(cost, (int, float))
    
    def test_terraform_generation(self, engine):
        """Test Terraform blueprint generation"""
        requirements = {
            "infrastructure_type": "terraform",
            "cloud_provider": "aws",
            "services": ["ec2", "rds", "s3"]
        }
        
        terraform = engine.generate_terraform(requirements)
        
        assert terraform is not None
        assert "resource" in terraform
        assert "aws_instance" in terraform


class TestVishnutOrchestration:
    """Test suite for Vishnu Orchestration Engine"""
    
    @pytest.fixture
    def engine(self):
        """Vishnu engine fixture"""
        return OrchestrationEngine()
    
    def test_policy_validation(self, engine):
        """Test policy validation"""
        policy = {
            "name": "test_policy",
            "rules": [
                {"condition": "cpu_usage > 80", "action": "scale_up"},
                {"condition": "error_rate > 5", "action": "restart_service"}
            ]
        }
        
        result = engine.validate_policy(policy)
        
        assert result["valid"] is True
        assert "compliance_score" in result
        assert result["compliance_score"] >= 0
    
    def test_workflow_execution(self, engine):
        """Test workflow execution"""
        workflow = {
            "name": "deployment_workflow",
            "steps": [
                {"name": "build", "action": "docker_build"},
                {"name": "test", "action": "run_tests"},
                {"name": "deploy", "action": "kubectl_apply"}
            ]
        }
        
        result = engine.execute_workflow(workflow)
        
        assert result["status"] in ["running", "completed", "failed"]
        assert "execution_id" in result
    
    def test_compliance_check(self, engine):
        """Test compliance checking"""
        config = {
            "security_policies": ["encryption", "access_control"],
            "data_retention": "90d",
            "backup_frequency": "daily"
        }
        
        compliance = engine.check_compliance(config)
        
        assert "score" in compliance
        assert compliance["score"] >= 0
        assert compliance["score"] <= 100


class TestShivaHealing:
    """Test suite for Shiva Healing Engine"""
    
    @pytest.fixture
    def engine(self):
        """Shiva engine fixture"""
        return HealingEngine()
    
    def test_anomaly_detection(self, engine):
        """Test anomaly detection"""
        metrics = {
            "cpu_usage": [45, 50, 48, 95, 52],  # One anomaly
            "memory_usage": [60, 65, 62, 68, 64],
            "response_time": [100, 110, 105, 108, 102]
        }
        
        anomalies = engine.detect_anomalies(metrics)
        
        assert len(anomalies) > 0
        assert "cpu_usage" in [a["metric"] for a in anomalies]
    
    def test_healing_plan_generation(self, engine):
        """Test healing plan generation"""
        incident = {
            "type": "high_cpu_usage",
            "affected_services": ["api-service"],
            "severity": "high",
            "metrics": {"cpu_usage": 95}
        }
        
        plan = engine.generate_healing_plan(incident)
        
        assert "actions" in plan
        assert len(plan["actions"]) > 0
        assert "estimated_time" in plan
    
    def test_auto_healing_execution(self, engine):
        """Test auto-healing execution"""
        healing_plan = {
            "actions": [
                {"type": "scale_up", "parameters": {"replicas": 2}},
                {"type": "restart_service", "parameters": {"service": "api"}}
            ]
        }
        
        result = engine.execute_healing(healing_plan)
        
        assert result["status"] in ["initiated", "running", "completed", "failed"]
        assert "execution_id" in result


class TestLakshmiFinOps:
    """Test suite for Lakshmi FinOps Engine"""
    
    @pytest.fixture
    def engine(self):
        """Lakshmi engine fixture"""
        return FinOpsEngine()
    
    def test_cost_analysis(self, engine):
        """Test cost analysis"""
        usage_data = {
            "compute": {"hours": 744, "cost_per_hour": 0.10},
            "storage": {"gb": 1000, "cost_per_gb": 0.023},
            "network": {"gb": 500, "cost_per_gb": 0.09}
        }
        
        analysis = engine.analyze_costs(usage_data)
        
        assert "total_cost" in analysis
        assert "breakdown" in analysis
        assert analysis["total_cost"] > 0
    
    def test_optimization_suggestions(self, engine):
        """Test optimization suggestions"""
        current_usage = {
            "instances": [
                {"type": "t3.large", "utilization": 30, "cost": 100},
                {"type": "t3.xlarge", "utilization": 85, "cost": 200}
            ]
        }
        
        suggestions = engine.get_optimization_suggestions(current_usage)
        
        assert len(suggestions) > 0
        assert all("potential_savings" in s for s in suggestions)
    
    def test_budget_monitoring(self, engine):
        """Test budget monitoring"""
        budget = {
            "monthly_limit": 5000,
            "current_spend": 3500,
            "forecast": 4800
        }
        
        status = engine.monitor_budget(budget)
        
        assert "status" in status
        assert "utilization_percentage" in status
        assert "days_remaining" in status


class TestKaliSecurity:
    """Test suite for Kali Security Engine"""
    
    @pytest.fixture
    def engine(self):
        """Kali engine fixture"""
        return SecurityEngine()
    
    def test_vulnerability_scanning(self, engine):
        """Test vulnerability scanning"""
        target = {
            "type": "network",
            "range": "10.0.1.0/24",
            "ports": [22, 80, 443, 3306]
        }
        
        scan_results = engine.scan_vulnerabilities(target)
        
        assert "scan_id" in scan_results
        assert "vulnerabilities" in scan_results
        assert "timestamp" in scan_results
    
    def test_threat_detection(self, engine):
        """Test threat detection"""
        logs = [
            {"timestamp": "2025-01-01T10:00:00Z", "source_ip": "192.168.1.100", "action": "login", "status": "success"},
            {"timestamp": "2025-01-01T10:01:00Z", "source_ip": "192.168.1.100", "action": "login", "status": "failed"},
            {"timestamp": "2025-01-01T10:02:00Z", "source_ip": "192.168.1.100", "action": "login", "status": "failed"},
            {"timestamp": "2025-01-01T10:03:00Z", "source_ip": "192.168.1.100", "action": "login", "status": "failed"}
        ]
        
        threats = engine.detect_threats(logs)
        
        assert len(threats) > 0
        assert "threat_type" in threats[0]
        assert "severity" in threats[0]
    
    def test_policy_enforcement(self, engine):
        """Test security policy enforcement"""
        policy = {
            "max_failed_logins": 3,
            "lockout_duration": 300,
            "required_tls_version": "1.2"
        }
        
        violation = {
            "type": "failed_login_attempt",
            "source_ip": "192.168.1.100",
            "attempts": 4
        }
        
        enforcement = engine.enforce_policy(policy, violation)
        
        assert "action" in enforcement
        assert "reason" in enforcement


class TestMLOpsIntegration:
    """Test suite for MLOps integration"""
    
    @pytest.fixture
    def model_manager(self):
        """MLflow model manager fixture"""
        with patch('mlflow.set_tracking_uri'):
            return MLflowModelManager("http://test-mlflow:5000")
    
    @pytest.fixture
    def anomaly_model(self, model_manager):
        """Anomaly detection model fixture"""
        return AnomalyDetectionModel(model_manager)
    
    def test_model_training(self, anomaly_model):
        """Test model training"""
        # Create sample training data
        training_data = pd.DataFrame({
            "cpu_usage": np.random.normal(50, 15, 100),
            "memory_usage": np.random.normal(60, 20, 100),
            "network_io": np.random.normal(100, 30, 100),
            "disk_io": np.random.normal(80, 25, 100)
        })
        
        with patch.object(anomaly_model.model_manager, 'log_model', return_value="test_run_id"):
            with patch.object(anomaly_model.model_manager, 'register_model', return_value="1"):
                version = anomaly_model.train_model(training_data)
                assert version == "1"
    
    def test_anomaly_prediction(self, anomaly_model):
        """Test anomaly prediction"""
        # Create sample data
        test_data = pd.DataFrame({
            "cpu_usage": [45, 50, 95, 52],  # One anomaly
            "memory_usage": [60, 65, 68, 64],
            "network_io": [100, 110, 105, 108],
            "disk_io": [80, 85, 88, 82]
        })
        
        with patch.object(anomaly_model.model_manager, 'load_model') as mock_load:
            mock_model = Mock()
            mock_model.predict.return_value = np.array([1, 1, -1, 1])  # One anomaly
            mock_load.return_value = mock_model
            
            result = anomaly_model.predict(test_data)
            
            assert "predictions" in result
            assert "anomaly_count" in result
            assert result["anomaly_count"] == 1


class TestPerformanceMetrics:
    """Test suite for performance metrics"""
    
    def test_api_response_time(self):
        """Test API response time"""
        client = TestClient(app)
        
        import time
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        client = TestClient(app)
        
        import concurrent.futures
        import time
        
        def make_request():
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            return response.status_code, end_time - start_time
        
        # Test with 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        status_codes = [result[0] for result in results]
        response_times = [result[1] for result in results]
        
        assert all(code == 200 for code in status_codes)
        assert all(time < 2.0 for time in response_times)  # All under 2 seconds


# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
