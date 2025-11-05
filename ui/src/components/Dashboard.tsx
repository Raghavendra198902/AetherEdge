import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Heading,
  Text,
  Card,
  CardBody,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  Badge,
  Flex,
  Icon,
  useColorModeValue,
  VStack,
  HStack,
  Button,
  SimpleGrid,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { 
  Brain, 
  Shield, 
  DollarSign, 
  Activity, 
  Users, 
  Search,
  Zap,
  Eye,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

interface ModuleStatus {
  name: string;
  status: 'healthy' | 'warning' | 'critical';
  uptime: string;
  requests: number;
  lastCheck: string;
}

interface MetricData {
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

interface DashboardData {
  modules: ModuleStatus[];
  infrastructure: {
    activeResources: MetricData;
    totalCost: MetricData;
    securityScore: MetricData;
    knowledge: MetricData;
  };
  alerts: Array<{
    id: string;
    type: 'info' | 'warning' | 'error';
    title: string;
    description: string;
    timestamp: string;
  }>;
}

const moduleIcons: Record<string, any> = {
  'Saraswati Knowledge': Brain,
  'Lakshmi FinOps': DollarSign,
  'Kali Security': Shield,
  'Hanuman Agents': Users,
  'Ganesha RCA': Search,
  'Brahma Blueprint': Zap,
  'Vishnu Orchestrator': Activity,
  'Shiva Healer': Eye,
};

const statusColors: Record<string, string> = {
  healthy: 'green',
  warning: 'yellow',
  critical: 'red',
};

const Dashboard: React.FC = () => {
  const [selectedModule, setSelectedModule] = useState<string>('overview');
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  const { data: dashboardData, isLoading, error, refetch } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/api/v1/dashboard/status`);
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: moduleHealth } = useQuery({
    queryKey: ['moduleHealth'],
    queryFn: async () => {
      const modules = [
        'saraswati', 'lakshmi', 'kali', 'hanuman', 'ganesha', 
        'brahma', 'vishnu', 'shiva'
      ];
      
      const healthChecks = await Promise.allSettled(
        modules.map(async (module) => {
          try {
            const response = await axios.get(`${API_BASE_URL}/api/v1/${module}/health`, {
              timeout: 5000
            });
            return { module, status: 'healthy', data: response.data };
          } catch (error) {
            return { module, status: 'critical' as const, error: (error as Error).message };
          }
        })
      );
      
      return healthChecks;
    },
    refetchInterval: 15000,
  });

  // Default infrastructure data to prevent undefined access
  const defaultInfrastructure = {
    activeResources: { value: 0, change: 0, trend: 'stable' as const },
    totalCost: { value: 0, change: 0, trend: 'stable' as const },
    securityScore: { value: 95, change: 0, trend: 'stable' as const },
    knowledge: { value: 0, change: 0, trend: 'stable' as const }
  };

  // Safe access to infrastructure data
  const infrastructure = dashboardData?.infrastructure || defaultInfrastructure;

  if (isLoading) {
    return (
      <Flex justify="center" align="center" h="100vh">
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text>Loading Divine Dashboard...</Text>
        </VStack>
      </Flex>
    );
  }

  if (error) {
    return (
      <Alert status="error" m={4}>
        <AlertIcon />
        <Box>
          <AlertTitle>Failed to load dashboard!</AlertTitle>
          <AlertDescription>
            Unable to connect to the AetherEdge API. Please check if all services are running.
          </AlertDescription>
        </Box>
        <Button ml="auto" onClick={() => refetch()}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box bg={bgColor} minH="100vh" p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="xl" color="blue.600" mb={2}>
            🌟 AetherEdge Divine Dashboard
          </Heading>
          <Text color="gray.600">
            Enterprise Infrastructure Automation Platform - Real-time Monitoring
          </Text>
        </Box>

        {/* Key Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card bg={cardBg} shadow="lg">
            <CardBody>
              <Stat>
                <StatLabel color="gray.600">Active Resources</StatLabel>
                <StatNumber color="blue.600">
                  {infrastructure.activeResources.value}
                </StatNumber>
                <StatHelpText color="green.500">
                  <Icon as={TrendingUp} boxSize={4} mr={1} />
                  +12% this week
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} shadow="lg">
            <CardBody>
              <Stat>
                <StatLabel color="gray.600">Monthly Cost</StatLabel>
                <StatNumber color="green.600">
                  ${infrastructure.totalCost.value.toLocaleString()}
                </StatNumber>
                <StatHelpText color="green.500">
                  <Icon as={TrendingUp} boxSize={4} mr={1} />
                  -8% optimized
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} shadow="lg">
            <CardBody>
              <Stat>
                <StatLabel color="gray.600">Security Score</StatLabel>
                <StatNumber color="purple.600">
                  {infrastructure.securityScore.value}%
                </StatNumber>
                <StatHelpText color="green.500">
                  <Icon as={CheckCircle} boxSize={4} mr={1} />
                  Excellent
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} shadow="lg">
            <CardBody>
              <Stat>
                <StatLabel color="gray.600">Knowledge Base</StatLabel>
                <StatNumber color="orange.600">
                  {infrastructure.knowledge.value} docs
                </StatNumber>
                <StatHelpText color="blue.500">
                  <Icon as={Brain} boxSize={4} mr={1} />
                  AI-powered
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Module Status Grid */}
        <Card bg={cardBg} shadow="lg">
          <CardBody>
            <Heading size="md" mb={4} color="gray.700">
              🕉️ Divine Module Status
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
              {moduleHealth?.map((result, index) => {
                const isSuccess = result.status === 'fulfilled';
                const moduleName = isSuccess ? 
                  (result.value as any)?.module || `Module ${index + 1}` :
                  `Module ${index + 1}`;
                const status = isSuccess ? 
                  (result.value as any)?.status || 'critical' : 'critical';
                const IconComponent = moduleIcons[moduleName] || Activity;
                
                return (
                  <Box
                    key={moduleName}
                    p={4}
                    borderRadius="lg"
                    bg={`${statusColors[status]}.50`}
                    border="1px"
                    borderColor={`${statusColors[status]}.200`}
                    cursor="pointer"
                    _hover={{ transform: 'translateY(-2px)', shadow: 'md' }}
                    transition="all 0.2s"
                    onClick={() => setSelectedModule(moduleName)}
                  >
                    <VStack spacing={2}>
                      <Icon as={IconComponent} size="24px" color={`${statusColors[status]}.600`} />
                      <Text fontWeight="bold" fontSize="sm" textAlign="center">
                        {moduleName}
                      </Text>
                      <Badge colorScheme={statusColors[status]} size="sm">
                        {status.toUpperCase()}
                      </Badge>
                      {status === 'healthy' && (
                        <Progress
                          value={95}
                          size="sm"
                          colorScheme="green"
                          w="100%"
                        />
                      )}
                    </VStack>
                  </Box>
                );
              })}
            </SimpleGrid>
          </CardBody>
        </Card>

        {/* Recent Alerts */}
        <Card bg={cardBg} shadow="lg">
          <CardBody>
            <Flex justify="space-between" align="center" mb={4}>
              <Heading size="md" color="gray.700">
                🚨 Recent Alerts
              </Heading>
              <Badge colorScheme="blue">Live</Badge>
            </Flex>
            <VStack spacing={3} align="stretch">
              {dashboardData?.alerts?.slice(0, 5).map((alert) => (
                <Alert key={alert.id} status={alert.type} borderRadius="md">
                  <AlertIcon />
                  <Box flex="1">
                    <AlertTitle fontSize="sm">{alert.title}</AlertTitle>
                    <AlertDescription fontSize="xs">
                      {alert.description}
                    </AlertDescription>
                  </Box>
                  <Text fontSize="xs" color="gray.500">
                    <Icon as={Clock} boxSize={3} mr={1} />
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </Text>
                </Alert>
              )) || (
                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>All systems operational</AlertTitle>
                  <AlertDescription>No active alerts at this time.</AlertDescription>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* Action Buttons */}
        <HStack spacing={4} justify="center">
          <Button 
            colorScheme="blue" 
            leftIcon={<Icon as={Activity} />}
            onClick={() => window.open(`${API_BASE_URL}/docs`, '_blank')}
          >
            API Documentation
          </Button>
          <Button 
            colorScheme="green" 
            leftIcon={<Icon as={Eye} />}
            onClick={() => setSelectedModule('monitoring')}
          >
            Detailed Monitoring
          </Button>
          <Button 
            colorScheme="purple" 
            leftIcon={<Icon as={Shield} />}
            onClick={() => setSelectedModule('security')}
          >
            Security Center
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export default Dashboard;
