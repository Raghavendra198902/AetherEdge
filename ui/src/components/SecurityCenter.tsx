import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  Badge,
  Progress,
  Heading,
  SimpleGrid,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Icon,
  Button,
  useColorModeValue,
} from '@chakra-ui/react';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  Zap,
} from 'lucide-react';

interface SecurityMetrics {
  overallScore: number;
  activeThreats: number;
  resolvedThreats: number;
  vulnerabilities: number;
  complianceScore: number;
}

interface SecurityAlert {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  timestamp: string;
  status: 'open' | 'investigating' | 'resolved';
}

interface SecurityCenterProps {
  metrics?: SecurityMetrics;
  alerts?: SecurityAlert[];
  isLoading?: boolean;
}

const severityColors = {
  low: 'green',
  medium: 'yellow',
  high: 'orange',
  critical: 'red',
};

const SecurityCenter: React.FC<SecurityCenterProps> = ({ 
  metrics = {
    overallScore: 95,
    activeThreats: 2,
    resolvedThreats: 47,
    vulnerabilities: 3,
    complianceScore: 92,
  },
  alerts = [
    {
      id: '1',
      severity: 'medium',
      title: 'Unusual API Access Pattern',
      description: 'Detected elevated API requests from new geographic region',
      timestamp: new Date().toISOString(),
      status: 'investigating',
    },
    {
      id: '2',
      severity: 'low',
      title: 'Certificate Expiring Soon',
      description: 'SSL certificate for api.aetheredge.com expires in 30 days',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      status: 'open',
    },
  ],
  isLoading = false,
}) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  if (isLoading) {
    return (
      <Box p={6}>
        <VStack spacing={4}>
          <Progress size="lg" isIndeterminate colorScheme="purple" w="100%" />
          <Text>Loading security data...</Text>
        </VStack>
      </Box>
    );
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <VStack align="start" spacing={1}>
            <Heading size="lg" color="purple.600">
              🛡️ Kali Security Center
            </Heading>
            <Text color="gray.600">
              Advanced threat detection and compliance monitoring
            </Text>
          </VStack>
          <HStack>
            <Button leftIcon={<Eye />} size="sm" variant="outline">
              View Logs
            </Button>
            <Button leftIcon={<Zap />} size="sm" colorScheme="purple">
              Run Scan
            </Button>
          </HStack>
        </HStack>

        {/* Security Score Overview */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 5 }} spacing={4}>
          <Card bg={cardBg}>
            <CardBody textAlign="center">
              <VStack spacing={2}>
                <Icon as={Shield} size="24px" color="purple.500" />
                <Text fontSize="2xl" fontWeight="bold" color="purple.600">
                  {metrics.overallScore}%
                </Text>
                <Text fontSize="sm" color="gray.600">Security Score</Text>
                <Progress
                  value={metrics.overallScore}
                  colorScheme="purple"
                  size="sm"
                  w="100%"
                />
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg}>
            <CardBody textAlign="center">
              <VStack spacing={2}>
                <Icon as={AlertTriangle} size="24px" color="red.500" />
                <Text fontSize="2xl" fontWeight="bold" color="red.600">
                  {metrics.activeThreats}
                </Text>
                <Text fontSize="sm" color="gray.600">Active Threats</Text>
                <Badge colorScheme="red" size="sm">
                  {metrics.activeThreats > 0 ? 'REQUIRES ATTENTION' : 'CLEAR'}
                </Badge>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg}>
            <CardBody textAlign="center">
              <VStack spacing={2}>
                <Icon as={CheckCircle} size="24px" color="green.500" />
                <Text fontSize="2xl" fontWeight="bold" color="green.600">
                  {metrics.resolvedThreats}
                </Text>
                <Text fontSize="sm" color="gray.600">Resolved Today</Text>
                <Badge colorScheme="green" size="sm">
                  AUTO-RESOLVED
                </Badge>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg}>
            <CardBody textAlign="center">
              <VStack spacing={2}>
                <Icon as={Eye} size="24px" color="orange.500" />
                <Text fontSize="2xl" fontWeight="bold" color="orange.600">
                  {metrics.vulnerabilities}
                </Text>
                <Text fontSize="sm" color="gray.600">Vulnerabilities</Text>
                <Badge colorScheme="orange" size="sm">
                  MONITORING
                </Badge>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg}>
            <CardBody textAlign="center">
              <VStack spacing={2}>
                <Icon as={CheckCircle} size="24px" color="blue.500" />
                <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                  {metrics.complianceScore}%
                </Text>
                <Text fontSize="sm" color="gray.600">Compliance</Text>
                <Progress
                  value={metrics.complianceScore}
                  colorScheme="blue"
                  size="sm"
                  w="100%"
                />
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Active Alerts */}
        <Card bg={cardBg} border="1px" borderColor={borderColor}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Heading size="md" color="gray.700">
                  🚨 Active Security Alerts
                </Heading>
                <Badge colorScheme="purple">Live Monitoring</Badge>
              </HStack>

              {alerts.length > 0 ? (
                <VStack spacing={3} align="stretch">
                  {alerts.map((alert) => (
                    <Alert
                      key={alert.id}
                      status={alert.severity === 'critical' || alert.severity === 'high' ? 'error' : 
                              alert.severity === 'medium' ? 'warning' : 'info'}
                      borderRadius="md"
                      border="1px"
                      borderColor={`${severityColors[alert.severity]}.200`}
                    >
                      <AlertIcon />
                      <Box flex="1">
                        <HStack justify="space-between" mb={1}>
                          <AlertTitle fontSize="sm" color="gray.800">
                            {alert.title}
                          </AlertTitle>
                          <HStack spacing={2}>
                            <Badge colorScheme={severityColors[alert.severity]} size="sm">
                              {alert.severity.toUpperCase()}
                            </Badge>
                            <Badge colorScheme="gray" size="sm">
                              {alert.status.toUpperCase()}
                            </Badge>
                          </HStack>
                        </HStack>
                        <AlertDescription fontSize="xs" color="gray.600">
                          {alert.description}
                        </AlertDescription>
                      </Box>
                      <VStack spacing={1} align="end">
                        <Text fontSize="xs" color="gray.500">
                          <Clock size={12} style={{ display: 'inline', marginRight: 4 }} />
                          {new Date(alert.timestamp).toLocaleTimeString()}
                        </Text>
                        <Button size="xs" colorScheme="purple" variant="outline">
                          Investigate
                        </Button>
                      </VStack>
                    </Alert>
                  ))}
                </VStack>
              ) : (
                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>All Clear!</AlertTitle>
                    <AlertDescription>
                      No active security alerts at this time. All systems are secure.
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>

        {/* Quick Actions */}
        <HStack spacing={4} justify="center">
          <Button colorScheme="purple" leftIcon={<Shield />}>
            Threat Hunt
          </Button>
          <Button colorScheme="blue" leftIcon={<Eye />} variant="outline">
            Security Audit
          </Button>
          <Button colorScheme="orange" leftIcon={<Zap />} variant="outline">
            Penetration Test
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export default SecurityCenter;
