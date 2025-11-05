import pytest
import asyncio
import httpx
import os
from typing import AsyncGenerator
import time

# Test configuration
API_BASE_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8000")
TIMEOUT = 30.0

class TestConfig:
    """Test configuration and constants"""
    BASE_URL = API_BASE_URL
    TIMEOUT = TIMEOUT
    
    # Expected response times (in seconds)
    MAX_RESPONSE_TIME = 1.0
    MAX_SEARCH_TIME = 2.0
    MAX_ANALYSIS_TIME = 5.0
    
    # Test data
    SAMPLE_QUERIES = [
        "infrastructure automation best practices",
        "cloud cost optimization strategies",
        "security threat detection",
        "incident response procedures",
        "deployment automation",
    ]
    
    SAMPLE_BLUEPRINT = {
        "name": "test-web-app",
        "environment": "production",
        "requirements": {
            "compute": "medium",
            "storage": "100GB",
            "network": "standard",
            "security": "high"
        }
    }

@pytest.fixture(scope="session")
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an HTTP client for testing"""
    timeout = httpx.Timeout(TIMEOUT)
    async with httpx.AsyncClient(timeout=timeout) as client:
        yield client

@pytest.fixture(scope="session")
async def api_client(http_client: httpx.AsyncClient) -> httpx.AsyncClient:
    """Configure API client with base URL"""
    http_client.base_url = TestConfig.BASE_URL
    return http_client

class TestSystemHealth:
    """Test overall system health and availability"""
    
    async def test_api_gateway_health(self, api_client: httpx.AsyncClient):
        """Test API Gateway health endpoint"""
        response = await api_client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "timestamp" in health_data
        assert "version" in health_data
    
    async def test_all_modules_health(self, api_client: httpx.AsyncClient):
        """Test health of all divine modules"""
        modules = [
            "saraswati", "lakshmi", "kali", "hanuman", 
            "ganesha", "brahma", "vishnu", "shiva"
        ]
        
        for module in modules:
            response = await api_client.get(f"/api/{module}/health")
            assert response.status_code == 200, f"{module} health check failed"
            
            health_data = response.json()
            assert health_data["status"] in ["healthy", "degraded"], f"{module} is unhealthy"
    
    async def test_database_connectivity(self, api_client: httpx.AsyncClient):
        """Test database connectivity through API"""
        response = await api_client.get("/api/health/database")
        assert response.status_code == 200
        
        db_health = response.json()
        assert db_health["postgres"]["status"] == "connected"
        assert db_health["redis"]["status"] == "connected"

class TestAPIPerformance:
    """Test API performance and response times"""
    
    async def test_dashboard_response_time(self, api_client: httpx.AsyncClient):
        """Test dashboard API response time"""
        start_time = time.time()
        response = await api_client.get("/api/dashboard/status")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < TestConfig.MAX_RESPONSE_TIME
    
    async def test_concurrent_requests(self, api_client: httpx.AsyncClient):
        """Test system under concurrent load"""
        async def make_request():
            response = await api_client.get("/health")
            return response.status_code
        
        # Create 20 concurrent requests
        tasks = [make_request() for _ in range(20)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    async def test_large_response_handling(self, api_client: httpx.AsyncClient):
        """Test handling of large responses"""
        response = await api_client.get("/api/metrics/all")
        assert response.status_code == 200
        
        # Response should not be empty and should be properly formatted JSON
        data = response.json()
        assert isinstance(data, (list, dict))
        assert len(response.content) > 0

class TestSaraswatiKnowledge:
    """Test Saraswati Knowledge Engine functionality"""
    
    async def test_knowledge_search(self, api_client: httpx.AsyncClient):
        """Test knowledge search functionality"""
        for query in TestConfig.SAMPLE_QUERIES:
            start_time = time.time()
            response = await api_client.post(
                "/api/saraswati/search",
                json={"query": query}
            )
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < TestConfig.MAX_SEARCH_TIME
            
            results = response.json()
            assert isinstance(results, list)
    
    async def test_knowledge_stats(self, api_client: httpx.AsyncClient):
        """Test knowledge statistics endpoint"""
        response = await api_client.get("/api/saraswati/stats")
        assert response.status_code == 200
        
        stats = response.json()
        assert "totalDocuments" in stats
        assert "categoriesCount" in stats
        assert "avgAccuracy" in stats
        assert stats["totalDocuments"] >= 0

class TestLakshmiFinOps:
    """Test Lakshmi FinOps Engine functionality"""
    
    async def test_cost_analysis(self, api_client: httpx.AsyncClient):
        """Test cost analysis functionality"""
        response = await api_client.get("/api/lakshmi/costs")
        assert response.status_code == 200
        
        cost_data = response.json()
        assert isinstance(cost_data, list)
        
        if cost_data:  # If there's data
            assert "service" in cost_data[0]
            assert "cost" in cost_data[0]
    
    async def test_cost_optimization(self, api_client: httpx.AsyncClient):
        """Test cost optimization recommendations"""
        response = await api_client.get("/api/lakshmi/optimization")
        assert response.status_code == 200
        
        optimization = response.json()
        assert "recommendations" in optimization or "opportunities" in optimization

class TestKaliSecurity:
    """Test Kali Security Engine functionality"""
    
    async def test_security_alerts(self, api_client: httpx.AsyncClient):
        """Test security alerts retrieval"""
        response = await api_client.get("/api/kali/alerts")
        assert response.status_code == 200
        
        alerts = response.json()
        assert isinstance(alerts, list)
    
    async def test_security_score(self, api_client: httpx.AsyncClient):
        """Test security score calculation"""
        response = await api_client.get("/api/kali/score")
        assert response.status_code == 200
        
        score_data = response.json()
        assert "score" in score_data
        assert 0 <= score_data["score"] <= 100

class TestHanumanAgents:
    """Test Hanuman Agents Engine functionality"""
    
    async def test_agent_status(self, api_client: httpx.AsyncClient):
        """Test agent status retrieval"""
        response = await api_client.get("/api/hanuman/agents")
        assert response.status_code == 200
        
        agents = response.json()
        assert isinstance(agents, list)
    
    async def test_agent_deployment(self, api_client: httpx.AsyncClient):
        """Test agent deployment functionality"""
        deployment_config = {
            "name": "test-agent",
            "type": "monitoring",
            "target": "test-environment"
        }
        
        response = await api_client.post("/api/hanuman/deploy", json=deployment_config)
        assert response.status_code in [200, 201, 202]  # Accept various success codes

class TestGaneshaRCA:
    """Test Ganesha RCA Engine functionality"""
    
    async def test_incidents_retrieval(self, api_client: httpx.AsyncClient):
        """Test incident retrieval"""
        response = await api_client.get("/api/ganesha/incidents")
        assert response.status_code == 200
        
        incidents = response.json()
        assert isinstance(incidents, list)
    
    async def test_incident_analysis(self, api_client: httpx.AsyncClient):
        """Test incident analysis (if incidents exist)"""
        # First get incidents
        response = await api_client.get("/api/ganesha/incidents")
        incidents = response.json()
        
        if incidents:
            incident_id = incidents[0].get("id")
            if incident_id:
                start_time = time.time()
                response = await api_client.post(f"/api/ganesha/analyze/{incident_id}")
                end_time = time.time()
                
                assert response.status_code == 200
                assert (end_time - start_time) < TestConfig.MAX_ANALYSIS_TIME

class TestBrahmaBlueprint:
    """Test Brahma Blueprint Engine functionality"""
    
    async def test_infrastructure_overview(self, api_client: httpx.AsyncClient):
        """Test infrastructure overview"""
        response = await api_client.get("/api/brahma/overview")
        assert response.status_code == 200
        
        overview = response.json()
        assert isinstance(overview, dict)
    
    async def test_blueprint_generation(self, api_client: httpx.AsyncClient):
        """Test blueprint generation"""
        start_time = time.time()
        response = await api_client.post(
            "/api/brahma/generate",
            json=TestConfig.SAMPLE_BLUEPRINT
        )
        end_time = time.time()
        
        assert response.status_code in [200, 201, 202]
        assert (end_time - start_time) < TestConfig.MAX_ANALYSIS_TIME

class TestVishnuOrchestrator:
    """Test Vishnu Orchestrator functionality"""
    
    async def test_workflows_retrieval(self, api_client: httpx.AsyncClient):
        """Test workflow retrieval"""
        response = await api_client.get("/api/vishnu/workflows")
        assert response.status_code == 200
        
        workflows = response.json()
        assert isinstance(workflows, list)

class TestShivaHealer:
    """Test Shiva Healer functionality"""
    
    async def test_anomalies_detection(self, api_client: httpx.AsyncClient):
        """Test anomaly detection"""
        response = await api_client.get("/api/shiva/anomalies")
        assert response.status_code == 200
        
        anomalies = response.json()
        assert isinstance(anomalies, list)

class TestIntegrationScenarios:
    """Test complete user scenarios across multiple modules"""
    
    async def test_complete_admin_workflow(self, api_client: httpx.AsyncClient):
        """Test complete admin workflow"""
        # 1. Check dashboard
        response = await api_client.get("/api/dashboard/status")
        assert response.status_code == 200
        
        # 2. Check security
        response = await api_client.get("/api/kali/alerts")
        assert response.status_code == 200
        
        # 3. Check costs
        response = await api_client.get("/api/lakshmi/costs")
        assert response.status_code == 200
        
        # 4. Check agents
        response = await api_client.get("/api/hanuman/agents")
        assert response.status_code == 200
    
    async def test_developer_workflow(self, api_client: httpx.AsyncClient):
        """Test developer workflow"""
        # 1. Search knowledge base
        response = await api_client.post(
            "/api/saraswati/search",
            json={"query": "deployment best practices"}
        )
        assert response.status_code == 200
        
        # 2. Generate blueprint
        response = await api_client.post(
            "/api/brahma/generate",
            json=TestConfig.SAMPLE_BLUEPRINT
        )
        assert response.status_code in [200, 201, 202]
        
        # 3. Check workflows
        response = await api_client.get("/api/vishnu/workflows")
        assert response.status_code == 200

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    async def test_invalid_endpoints(self, api_client: httpx.AsyncClient):
        """Test invalid endpoint handling"""
        response = await api_client.get("/api/nonexistent")
        assert response.status_code == 404
    
    async def test_invalid_request_data(self, api_client: httpx.AsyncClient):
        """Test invalid request data handling"""
        response = await api_client.post(
            "/api/saraswati/search",
            json={"invalid": "data"}
        )
        assert response.status_code in [400, 422]  # Bad request or validation error
    
    async def test_large_payload_handling(self, api_client: httpx.AsyncClient):
        """Test large payload handling"""
        large_payload = {"data": "x" * 10000}  # 10KB payload
        response = await api_client.post("/api/saraswati/search", json=large_payload)
        assert response.status_code in [200, 400, 413]  # Success, bad request, or payload too large

# Performance benchmarks
@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    async def test_api_response_times(self, api_client: httpx.AsyncClient):
        """Benchmark API response times"""
        endpoints = [
            "/health",
            "/api/dashboard/status",
            "/api/saraswati/stats",
            "/api/lakshmi/costs",
            "/api/kali/score",
        ]
        
        results = {}
        for endpoint in endpoints:
            start_time = time.time()
            response = await api_client.get(endpoint)
            end_time = time.time()
            
            results[endpoint] = end_time - start_time
            assert response.status_code == 200
        
        # Log results for analysis
        print("\nAPI Response Times:")
        for endpoint, duration in results.items():
            print(f"{endpoint}: {duration:.3f}s")
            assert duration < TestConfig.MAX_RESPONSE_TIME
