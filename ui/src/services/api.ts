import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      // Redirect to login page or handle authentication error
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface HealthStatus {
  service: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  uptime: number;
  responseTime: number;
  lastCheck: string;
  version: string;
}

export interface ModuleMetrics {
  module: string;
  requests: number;
  errors: number;
  avgResponseTime: number;
  cpu: number;
  memory: number;
  timestamp: string;
}

export interface SecurityAlert {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  source: string;
  timestamp: string;
  status: 'open' | 'investigating' | 'resolved';
}

export interface CostData {
  service: string;
  cost: number;
  change: number;
  currency: 'USD';
  period: 'daily' | 'weekly' | 'monthly';
}

export interface KnowledgeStats {
  totalDocuments: number;
  categoriesCount: number;
  avgAccuracy: number;
  searchQueries: number;
  lastUpdated: string;
}

// API Service Functions
export const apiService = {
  // Health Check APIs
  async getOverallHealth(): Promise<HealthStatus[]> {
    const response = await api.get('/api/health/all');
    return response.data;
  },

  async getModuleHealth(module: string): Promise<HealthStatus> {
    const response = await api.get(`/api/${module}/health`);
    return response.data;
  },

  // Metrics APIs
  async getModuleMetrics(module: string, timeRange: string = '1h'): Promise<ModuleMetrics[]> {
    const response = await api.get(`/api/${module}/metrics?range=${timeRange}`);
    return response.data;
  },

  async getAllModuleMetrics(): Promise<ModuleMetrics[]> {
    const response = await api.get('/api/metrics/all');
    return response.data;
  },

  // Security APIs
  async getSecurityAlerts(limit: number = 10): Promise<SecurityAlert[]> {
    const response = await api.get(`/api/kali/alerts?limit=${limit}`);
    return response.data;
  },

  async getSecurityScore(): Promise<{ score: number; details: any }> {
    const response = await api.get('/api/kali/score');
    return response.data;
  },

  // FinOps APIs
  async getCostAnalysis(): Promise<CostData[]> {
    const response = await api.get('/api/lakshmi/costs');
    return response.data;
  },

  async getCostOptimization(): Promise<any> {
    const response = await api.get('/api/lakshmi/optimization');
    return response.data;
  },

  // Knowledge APIs
  async getKnowledgeStats(): Promise<KnowledgeStats> {
    const response = await api.get('/api/saraswati/stats');
    return response.data;
  },

  async searchKnowledge(query: string): Promise<any[]> {
    const response = await api.post('/api/saraswati/search', { query });
    return response.data;
  },

  // Agent APIs
  async getAgentStatus(): Promise<any[]> {
    const response = await api.get('/api/hanuman/agents');
    return response.data;
  },

  async deployAgent(config: any): Promise<any> {
    const response = await api.post('/api/hanuman/deploy', config);
    return response.data;
  },

  // RCA APIs
  async getIncidents(): Promise<any[]> {
    const response = await api.get('/api/ganesha/incidents');
    return response.data;
  },

  async analyzeIncident(incidentId: string): Promise<any> {
    const response = await api.post(`/api/ganesha/analyze/${incidentId}`);
    return response.data;
  },

  // Infrastructure APIs
  async getInfrastructureOverview(): Promise<any> {
    const response = await api.get('/api/brahma/overview');
    return response.data;
  },

  async generateBlueprint(requirements: any): Promise<any> {
    const response = await api.post('/api/brahma/generate', requirements);
    return response.data;
  },

  // Orchestration APIs
  async getWorkflows(): Promise<any[]> {
    const response = await api.get('/api/vishnu/workflows');
    return response.data;
  },

  async executeWorkflow(workflowId: string, params: any): Promise<any> {
    const response = await api.post(`/api/vishnu/execute/${workflowId}`, params);
    return response.data;
  },

  // Healing APIs
  async getAnomalies(): Promise<any[]> {
    const response = await api.get('/api/shiva/anomalies');
    return response.data;
  },

  async triggerHealing(targetId: string): Promise<any> {
    const response = await api.post(`/api/shiva/heal/${targetId}`);
    return response.data;
  },
};

export default api;
