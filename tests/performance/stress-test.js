import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const apiResponseTime = new Trend('api_response_time');

// Stress test configuration
export const options = {
  stages: [
    { duration: '1m', target: 50 }, // Ramp-up to 50 users
    { duration: '2m', target: 200 }, // Ramp-up to 200 users  
    { duration: '5m', target: 500 }, // Stay at 500 users (stress)
    { duration: '2m', target: 1000 }, // Spike to 1000 users
    { duration: '1m', target: 0 }, // Ramp-down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests under 1s
    http_req_failed: ['rate<0.2'], // Error rate under 20% (stress test)
    errors: ['rate<0.2'], // Custom error rate under 20%
  },
};

// Base URL configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export function setup() {
  console.log('Starting AetherEdge Platform Stress Test');
  
  // Test if the API is accessible
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`API not accessible: ${healthCheck.status}`);
  }
  
  return { baseUrl: BASE_URL };
}

export default function (data) {
  const baseUrl = data.baseUrl;
  
  // Stress test with rapid requests
  group('Rapid Health Checks', () => {
    for (let i = 0; i < 5; i++) {
      const response = http.get(`${baseUrl}/health`);
      
      check(response, {
        'health check status is 200': (r) => r.status === 200,
      });
      
      errorRate.add(response.status !== 200);
      apiResponseTime.add(response.timings.duration);
      
      // No sleep between requests to stress the system
    }
  });
  
  // Memory intensive operations
  group('Heavy Blueprint Generation', () => {
    const largePayload = {
      infrastructure_type: 'kubernetes',
      requirements: {
        cpu: '32 cores',
        memory: '128GB',
        storage: '10TB',
        nodes: 100,
        services: Array.from({ length: 50 }, (_, i) => `service-${i}`)
      },
      cloud_provider: 'aws'
    };
    
    const headers = { 'Content-Type': 'application/json' };
    const response = http.post(
      `${baseUrl}/api/v1/brahma/generate-blueprint`,
      JSON.stringify(largePayload),
      { headers }
    );
    
    check(response, {
      'heavy blueprint status is 200 or 503': (r) => [200, 503].includes(r.status),
    });
    
    errorRate.add(![200, 503].includes(response.status));
  });
  
  // Short sleep to prevent overwhelming the system
  sleep(0.1);
}

export function teardown(data) {
  console.log('Stress test completed');
  
  // Wait a bit for system to recover
  sleep(5);
  
  // Final health check
  const finalCheck = http.get(`${data.baseUrl}/health`);
  console.log(`Final health check status: ${finalCheck.status}`);
}
