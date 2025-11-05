import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
export const errorRate = new Rate('errors');
export const responseTime = new Trend('response_time');

// Test configuration
export const options = {
  stages: [
    // Ramp-up
    { duration: '2m', target: 10 },   // Ramp up to 10 users over 2 minutes
    { duration: '5m', target: 10 },   // Stay at 10 users for 5 minutes
    { duration: '2m', target: 50 },   // Ramp up to 50 users over 2 minutes
    { duration: '10m', target: 50 },  // Stay at 50 users for 10 minutes
    { duration: '3m', target: 100 },  // Ramp up to 100 users over 3 minutes
    { duration: '15m', target: 100 }, // Stay at 100 users for 15 minutes
    { duration: '2m', target: 200 },  // Spike to 200 users over 2 minutes
    { duration: '5m', target: 200 },  // Stay at 200 users for 5 minutes
    { duration: '5m', target: 0 },    // Ramp down to 0 users over 5 minutes
  ],
  thresholds: {
    // Error rate should be less than 1%
    errors: ['rate<0.01'],
    // 95% of requests should be below 500ms
    http_req_duration: ['p(95)<500'],
    // 99% of requests should be below 1s
    'http_req_duration{expected_response:true}': ['p(99)<1000'],
    // Response time trend
    response_time: ['p(95)<500'],
  },
};

// Base URL - can be overridden via environment variable
const BASE_URL = __ENV.TARGET_URL || 'http://localhost:8000';

// Authentication token (if required)
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

// Test data - Using environment variables for security
const testUsers = [
  { email: 'admin@aetheredge.com', password: __ENV.TEST_ADMIN_PASSWORD || 'test-admin' },
  { email: 'user1@aetheredge.com', password: __ENV.TEST_USER_PASSWORD || 'test-user1' },
  { email: 'user2@aetheredge.com', password: __ENV.TEST_USER_PASSWORD || 'test-user2' },
];

const testQueries = [
  'infrastructure automation',
  'cloud optimization',
  'security monitoring',
  'cost analysis',
  'incident response',
  'deployment strategies',
];

const blueprintRequests = [
  {
    name: 'web-application',
    environment: 'production',
    requirements: {
      compute: 'medium',
      storage: '100GB',
      network: 'standard',
    },
  },
  {
    name: 'microservices',
    environment: 'staging',
    requirements: {
      compute: 'high',
      storage: '500GB',
      network: 'premium',
    },
  },
];

export function setup() {
  // Setup function runs once before the test
  console.log('Starting AetherEdge load test...');
  
  // Health check
  const healthResponse = http.get(`${BASE_URL}/health`);
  if (healthResponse.status !== 200) {
    throw new Error(`Health check failed: ${healthResponse.status}`);
  }
  
  console.log('Health check passed, starting test...');
  return { baseUrl: BASE_URL };
}

export default function (data) {
  const baseUrl = data.baseUrl;
  
  // Simulate different user behaviors
  const userBehavior = Math.random();
  
  if (userBehavior < 0.3) {
    // 30% - Admin/Power User workflow
    adminWorkflow(baseUrl);
  } else if (userBehavior < 0.6) {
    // 30% - Developer workflow
    developerWorkflow(baseUrl);
  } else if (userBehavior < 0.9) {
    // 30% - Analyst workflow
    analystWorkflow(baseUrl);
  } else {
    // 10% - Anonymous/Guest workflow
    guestWorkflow(baseUrl);
  }
  
  // Random sleep between 1-5 seconds
  sleep(Math.random() * 4 + 1);
}

function adminWorkflow(baseUrl) {
  const params = getRequestParams();
  
  // Dashboard overview
  let response = http.get(`${baseUrl}/api/dashboard/status`, params);
  checkResponse(response, 'Dashboard Status');
  
  // Security center
  response = http.get(`${baseUrl}/api/kali/alerts`, params);
  checkResponse(response, 'Security Alerts');
  
  // System metrics
  response = http.get(`${baseUrl}/api/metrics/all`, params);
  checkResponse(response, 'System Metrics');
  
  // Cost analysis
  response = http.get(`${baseUrl}/api/lakshmi/costs`, params);
  checkResponse(response, 'Cost Analysis');
  
  // Agent management
  response = http.get(`${baseUrl}/api/hanuman/agents`, params);
  checkResponse(response, 'Agent Status');
}

function developerWorkflow(baseUrl) {
  const params = getRequestParams();
  
  // API documentation
  let response = http.get(`${baseUrl}/docs`, params);
  checkResponse(response, 'API Documentation');
  
  // Blueprint generation
  const blueprintRequest = blueprintRequests[Math.floor(Math.random() * blueprintRequests.length)];
  response = http.post(`${baseUrl}/api/brahma/generate`, JSON.stringify(blueprintRequest), params);
  checkResponse(response, 'Blueprint Generation');
  
  // Knowledge search
  const query = testQueries[Math.floor(Math.random() * testQueries.length)];
  response = http.post(`${baseUrl}/api/saraswati/search`, JSON.stringify({ query }), params);
  checkResponse(response, 'Knowledge Search');
  
  // Workflow execution
  response = http.get(`${baseUrl}/api/vishnu/workflows`, params);
  checkResponse(response, 'Workflow List');
}

function analystWorkflow(baseUrl) {
  const params = getRequestParams();
  
  // Cost optimization
  let response = http.get(`${baseUrl}/api/lakshmi/optimization`, params);
  checkResponse(response, 'Cost Optimization');
  
  // Incident analysis
  response = http.get(`${baseUrl}/api/ganesha/incidents`, params);
  checkResponse(response, 'Incident List');
  
  // Security score
  response = http.get(`${baseUrl}/api/kali/score`, params);
  checkResponse(response, 'Security Score');
  
  // Anomaly detection
  response = http.get(`${baseUrl}/api/shiva/anomalies`, params);
  checkResponse(response, 'Anomaly Detection');
}

function guestWorkflow(baseUrl) {
  const params = getRequestParams();
  
  // Health check
  let response = http.get(`${baseUrl}/health`, params);
  checkResponse(response, 'Health Check');
  
  // Public metrics
  response = http.get(`${baseUrl}/metrics`, params);
  checkResponse(response, 'Public Metrics');
}

function getRequestParams() {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'K6 Load Test',
    },
    timeout: '30s',
  };
  
  if (AUTH_TOKEN) {
    params.headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  
  return params;
}

function checkResponse(response, operation) {
  const result = check(response, {
    [`${operation} - Status is 200`]: (r) => r.status === 200,
    [`${operation} - Response time < 1000ms`]: (r) => r.timings.duration < 1000,
    [`${operation} - Body is not empty`]: (r) => r.body.length > 0,
  });
  
  // Record custom metrics
  errorRate.add(!result);
  responseTime.add(response.timings.duration);
  
  if (!result) {
    console.error(`${operation} failed: ${response.status} - ${response.body}`);
  }
}

export function teardown(data) {
  console.log('Load test completed.');
}
