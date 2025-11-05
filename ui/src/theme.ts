import { extendTheme, type ThemeConfig } from '@chakra-ui/react';

const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: false,
};

const theme = extendTheme({
  config,
  colors: {
    brand: {
      50: '#e3f2fd',
      100: '#bbdefb',
      200: '#90caf9',
      300: '#64b5f6',
      400: '#42a5f5',
      500: '#2196f3',
      600: '#1e88e5',
      700: '#1976d2',
      800: '#1565c0',
      900: '#0d47a1',
    },
    divine: {
      brahma: '#FF6B35',     // Orange - Creation
      vishnu: '#2E86AB',     // Blue - Preservation
      shiva: '#A23B72',      // Purple - Transformation
      saraswati: '#F18F01',  // Yellow - Knowledge
      lakshmi: '#C73E1D',    // Red - Prosperity
      kali: '#000000',       // Black - Protection
      hanuman: '#FF8500',    // Orange - Service
      ganesha: '#8B4513',    // Brown - Remover of Obstacles
    },
  },
  fonts: {
    heading: 'Inter, sans-serif',
    body: 'Inter, sans-serif',
  },
  components: {
    Card: {
      baseStyle: {
        container: {
          boxShadow: 'lg',
          _hover: {
            boxShadow: 'xl',
            transform: 'translateY(-2px)',
          },
          transition: 'all 0.2s',
        },
      },
    },
    Button: {
      baseStyle: {
        fontWeight: 'semibold',
        borderRadius: 'lg',
      },
      variants: {
        divine: {
          bg: 'brand.500',
          color: 'white',
          _hover: {
            bg: 'brand.600',
            transform: 'translateY(-1px)',
            boxShadow: 'lg',
          },
        },
      },
    },
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
        color: 'gray.900',
      },
    },
  },
});

export default theme;
