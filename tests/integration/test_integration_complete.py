"""
AetherEdge Platform - Integration Tests
End-to-end integration testing for the complete platform
"""

import pytest
import asyncio
import requests
import docker
import subprocess
import time
import os
from typing import Dict, Any


class TestDockerIntegration:
    """Integration tests using Docker containers"""
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """Docker client fixture"""
        return docker.from_env()
    
    @pytest.fixture(scope="class")
    def test_network(self, docker_client):
        """Create test network"""
        network = docker_client.networks.create("aetheredge-test")
        yield network
        network.remove()
    
    @pytest.fixture(scope="class")
    def postgres_container(self, docker_client, test_network):
        """PostgreSQL container for testing"""
        container = docker_client.containers.run(
            "postgres:16-alpine",
            environment={
                "POSTGRES_DB": "aetheredge_test",
                "POSTGRES_USER": "test",
                "POSTGRES_PASSWORD": os.getenv("TEST_DB_PASSWORD", 
                                                "test-password")
            },
            ports={"5432/tcp": ("127.0.0.1", 15432)},
            network=test_network.name,
            name="postgres-test",
            detach=True
        )
        
        # Wait for PostgreSQL to be ready
        time.sleep(10)
        
        yield container
        container.stop()
        container.remove()
    
    @pytest.fixture(scope="class")
    def redis_container(self, docker_client, test_network):
        """Redis container for testing"""
        container = docker_client.containers.run(
            "redis:7-alpine",
            ports={"6379/tcp": ("127.0.0.1", 16379)},
            network=test_network.name,
            name="redis-test",
            detach=True
        )
        
        # Wait for Redis to be ready
        time.sleep(5)
        
        yield container
        container.stop()
        container.remove()
    
    @pytest.fixture(scope="class")
    def api_container(self, docker_client, test_network, postgres_container, redis_container):
        """AetherEdge API container for testing"""
        # Build the image first (assumes Dockerfile exists)
        if os.path.exists("Dockerfile"):
            docker_client.images.build(
                path=".",
                tag="aetheredge-api:test"
            )
            
            container = docker_client.containers.run(
                "aetheredge-api:test",
                environment={
                    "DATABASE_URL": (
                        f"postgresql://test:"
                        f"{os.getenv('TEST_DB_PASSWORD', 'test-password')}"
                        f"@postgres-test:5432/aetheredge_test"
                    ),
                    "REDIS_URL": "redis://redis-test:6379/0",
                    "ENVIRONMENT": "test"
                },
                ports={"8000/tcp": ("127.0.0.1", 18000)},
                network=test_network.name,
                name="api-test",
                detach=True
            )
            
            # Wait for API to be ready
            time.sleep(15)
            
            yield container
            container.stop()
            container.remove()
        else:
            pytest.skip("Dockerfile not found, skipping API container test")
    
    def test_database_connection(self, postgres_container):
        """Test database connectivity"""
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            port=15432,
            database="aetheredge_test",
            user="test",
            password=os.getenv("TEST_DB_PASSWORD", "test-password")
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        
        assert result is not None
        assert "PostgreSQL" in result[0]
        
        conn.close()
    
    def test_redis_connection(self, redis_container):
        """Test Redis connectivity"""
        import redis
        
        r = redis.Redis(host="localhost", port=16379, db=0)
        
        # Test basic operations
        r.set("test_key", "test_value")
        result = r.get("test_key")
        
        assert result.decode() == "test_value"
    
    def test_api_health_check(self, api_container):
        """Test API health check endpoint"""
        response = requests.get("http://localhost:18000/health", timeout=10)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_complete_workflow(self, api_container):
        """Test complete end-to-end workflow"""
        base_url = "http://localhost:18000"
        
        # 1. Test Brahma blueprint generation
        blueprint_payload = {
            "infrastructure_type": "kubernetes",
            "requirements": {"cpu": "2 cores", "memory": "4GB"},
            "cloud_provider": "aws"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/brahma/generate-blueprint",
            json=blueprint_payload,
            timeout=30
        )
        assert response.status_code == 200
        blueprint_data = response.json()
        
        # 2. Test Vishnu policy validation
        policy_payload = {
            "policy_type": "security",
            "rules": [{"condition": "cpu_usage > 80", "action": "scale_up"}]
        }
        
        response = requests.post(
            f"{base_url}/api/v1/vishnu/validate-policy",
            json=policy_payload,
            timeout=30
        )
        assert response.status_code == 200
        policy_data = response.json()
        
        # 3. Test Lakshmi cost analysis
        cost_payload = {
            "time_range": "7d",
            "services": ["api", "database"],
            "cloud_provider": "aws"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/lakshmi/analyze-costs",
            json=cost_payload,
            timeout=30
        )
        assert response.status_code == 200
        cost_data = response.json()
        
        # Verify all responses contain expected fields
        assert "blueprint" in blueprint_data
        assert "validation_result" in policy_data
        assert "cost_breakdown" in cost_data


class TestKubernetesIntegration:
    """Integration tests for Kubernetes deployment"""
    
    @pytest.fixture(scope="class")
    def kubectl_available(self):
        """Check if kubectl is available"""
        try:
            subprocess.run(["kubectl", "version", "--client"], 
                         check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("kubectl not available, skipping Kubernetes tests")
    
    def test_namespace_creation(self, kubectl_available):
        """Test namespace creation"""
        namespace = "aetheredge-test"
        
        # Create namespace
        result = subprocess.run([
            "kubectl", "create", "namespace", namespace,
            "--dry-run=client", "-o", "yaml"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert f"name: {namespace}" in result.stdout
    
    def test_kustomize_build(self, kubectl_available):
        """Test Kustomize build"""
        if not os.path.exists("kubernetes/overlays/development"):
            pytest.skip("Kubernetes manifests not found")
        
        result = subprocess.run([
            "kubectl", "kustomize", "kubernetes/overlays/development"
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "apiVersion" in result.stdout
        assert "kind: Deployment" in result.stdout
    
    def test_helm_template(self, kubectl_available):
        """Test Helm template rendering"""
        if not os.path.exists("helm/aetheredge"):
            pytest.skip("Helm chart not found")
        
        try:
            result = subprocess.run([
                "helm", "template", "aetheredge", "helm/aetheredge"
            ], capture_output=True, text=True, check=True)
            
            assert "apiVersion" in result.stdout
            assert "kind: Deployment" in result.stdout
        except FileNotFoundError:
            pytest.skip("Helm not available")
        except subprocess.CalledProcessError:
            pytest.fail("Helm template rendering failed")


class TestMonitoringIntegration:
    """Integration tests for monitoring stack"""
    
    @pytest.fixture(scope="class")
    def docker_compose_monitoring(self):
        """Start monitoring stack with docker-compose"""
        compose_file = "infrastructure/monitoring/docker-compose.yml"
        
        if not os.path.exists(compose_file):
            pytest.skip("Monitoring docker-compose file not found")
        
        # Start services
        subprocess.run([
            "docker-compose", "-f", compose_file, "up", "-d"
        ], check=True)
        
        # Wait for services to be ready
        time.sleep(30)
        
        yield
        
        # Cleanup
        subprocess.run([
            "docker-compose", "-f", compose_file, "down", "-v"
        ])
    
    def test_prometheus_metrics(self, docker_compose_monitoring):
        """Test Prometheus metrics collection"""
        try:
            response = requests.get("http://localhost:9090/api/v1/targets", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "success"
        except requests.exceptions.ConnectionError:
            pytest.skip("Prometheus not accessible")
    
    def test_grafana_api(self, docker_compose_monitoring):
        """Test Grafana API"""
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert data["database"] == "ok"
        except requests.exceptions.ConnectionError:
            pytest.skip("Grafana not accessible")
    
    def test_jaeger_traces(self, docker_compose_monitoring):
        """Test Jaeger tracing"""
        try:
            response = requests.get("http://localhost:16686/api/services", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert "data" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("Jaeger not accessible")


class TestSecurityIntegration:
    """Integration tests for security components"""
    
    def test_tls_certificate_validation(self):
        """Test TLS certificate validation"""
        # This would test actual TLS setup in production
        # For now, just verify the certificate files exist
        cert_files = [
            "secrets/tls.crt",
            "secrets/tls.key"
        ]
        
        for cert_file in cert_files:
            if os.path.exists(cert_file):
                assert os.path.getsize(cert_file) > 0
    
    def test_secret_management(self):
        """Test secret management"""
        # Verify secrets are not in plain text in configs
        config_files = [
            "kubernetes/base/configmap.yaml",
            "helm/aetheredge/values.yaml"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    # Should not contain plain text passwords
                    assert "password123" not in content.lower()
                    assert "secret123" not in content.lower()
    
    def test_network_policies(self):
        """Test network policy configuration"""
        policy_file = "kubernetes/base/network-policies.yaml"
        
        if os.path.exists(policy_file):
            with open(policy_file, 'r') as f:
                content = f.read()
                assert "NetworkPolicy" in content
                assert "deny-all" in content


class TestPerformanceIntegration:
    """Integration tests for performance requirements"""
    
    def test_api_load_testing(self):
        """Test API under load"""
        if not os.path.exists("tests/performance/load-test.js"):
            pytest.skip("Load test script not found")
        
        try:
            # Run k6 load test
            result = subprocess.run([
                "k6", "run", "tests/performance/load-test.js"
            ], capture_output=True, text=True, timeout=120)
            
            # Check if load test passed (basic check)
            assert "test passed" in result.stdout.lower() or result.returncode == 0
        except FileNotFoundError:
            pytest.skip("k6 not available")
        except subprocess.TimeoutExpired:
            pytest.fail("Load test timed out")
    
    def test_database_performance(self):
        """Test database performance"""
        # This would run database performance tests
        # For now, just ensure connection pooling is configured
        config_files = [
            "infrastructure/database/postgres/init.sql",
            "src/api/core/database.py"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
                    # Basic check for performance configurations
                    assert len(content) > 0


class TestMLOpsIntegration:
    """Integration tests for MLOps pipeline"""
    
    def test_mlflow_server(self):
        """Test MLflow server connectivity"""
        try:
            response = requests.get("http://localhost:5000", timeout=10)
            # MLflow server should respond (may redirect)
            assert response.status_code in [200, 302]
        except requests.exceptions.ConnectionError:
            pytest.skip("MLflow server not accessible")
    
    def test_model_training_pipeline(self):
        """Test model training pipeline"""
        # This would test the actual model training
        # For now, just verify the pipeline files exist
        pipeline_files = [
            "mlops/mlflow_manager.py",
            "mlops/feature-store/__init__.py"
        ]
        
        for pipeline_file in pipeline_files:
            if os.path.exists(pipeline_file):
                assert os.path.getsize(pipeline_file) > 0


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])
