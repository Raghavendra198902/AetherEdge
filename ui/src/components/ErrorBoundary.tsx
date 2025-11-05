import React, { Component, ReactNode } from 'react';
import {
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  VStack,
  Heading,
  Text,
  Box,
} from '@chakra-ui/react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Dashboard Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Box p={6} minH="100vh" bg="gray.50">
          <VStack spacing={6} align="center" justify="center" minH="60vh">
            <Alert status="error" maxW="600px">
              <AlertIcon />
              <Box>
                <AlertTitle>Something went wrong!</AlertTitle>
                <AlertDescription>
                  The dashboard encountered an unexpected error. Please refresh the page or contact support.
                </AlertDescription>
              </Box>
            </Alert>
            
            <VStack spacing={4}>
              <Heading size="md" color="gray.600">
                🚨 Dashboard Error
              </Heading>
              <Text color="gray.500" textAlign="center">
                Error: {this.state.error?.message || 'Unknown error occurred'}
              </Text>
              <Button 
                colorScheme="blue" 
                onClick={() => globalThis.location.reload()}
              >
                Refresh Page
              </Button>
            </VStack>
          </VStack>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
