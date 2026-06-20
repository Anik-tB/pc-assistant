import { createTheme, alpha } from '@mui/material';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#070C16',
      paper: 'rgba(11, 20, 38, 0.65)',
    },
    primary: {
      main: '#00F0FF', // Cyber Cyan
      light: '#5cffff',
      dark: '#00b8cc',
    },
    secondary: {
      main: '#FF003C', // Neon Magenta
      light: '#ff4c6c',
      dark: '#c2002e',
    },
    success: {
      main: '#00FF66', // Neon Green
    },
    error: {
      main: '#FF003C',
    },
    text: {
      primary: '#FFFFFF',
      secondary: 'rgba(255, 255, 255, 0.7)',
    }
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h2: {
      fontWeight: 800,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
      letterSpacing: '0.02em',
    }
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0, 240, 255, 0.1)',
          backgroundImage: 'linear-gradient(to bottom right, rgba(255,255,255,0.02), rgba(255,255,255,0))',
          boxShadow: '0 8px 32px 0 rgba(0, 240, 255, 0.05)',
        }
      }
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          transition: 'all 0.3s ease',
        },
        containedPrimary: {
          background: 'linear-gradient(135deg, #00F0FF 0%, #0080FF 100%)',
          color: '#070C16',
          boxShadow: '0 4px 20px rgba(0, 240, 255, 0.4)',
          '&:hover': {
            background: 'linear-gradient(135deg, #5cffff 0%, #00b8cc 100%)',
            boxShadow: '0 6px 25px rgba(0, 240, 255, 0.6)',
            transform: 'translateY(-2px)',
          }
        }
      }
    }
  }
});
