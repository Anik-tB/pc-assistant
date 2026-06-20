import React, { useEffect } from 'react';
import { ThemeProvider, CssBaseline, Box, Container, Grid } from '@mui/material';
import { theme } from './theme';
import { useAppStore } from './store/useAppStore';

import { Header } from './components/Header';
import { SystemStats } from './components/SystemStats';
import { PerformanceChart } from './components/PerformanceChart';
import { CommandTerminal } from './components/CommandTerminal';

function App() {
  const { connect, disconnect } = useAppStore();

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{
        minHeight: '100vh',
        background: 'radial-gradient(circle at 50% 50%, #0B1426 0%, #070C16 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Background Grid Pattern */}
        <Box sx={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          opacity: 0.03,
          backgroundImage: 'linear-gradient(#00F0FF 1px, transparent 1px), linear-gradient(90deg, #00F0FF 1px, transparent 1px)',
          backgroundSize: '30px 30px',
          pointerEvents: 'none'
        }} />

        {/* Glowing Orbs */}
        <Box sx={{
          position: 'absolute', top: '10%', left: '10%', width: '40vw', height: '40vw',
          background: 'radial-gradient(circle, rgba(0,240,255,0.05) 0%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none', filter: 'blur(40px)'
        }} />
        <Box sx={{
          position: 'absolute', bottom: '10%', right: '10%', width: '30vw', height: '30vw',
          background: 'radial-gradient(circle, rgba(255,0,60,0.05) 0%, rgba(0,0,0,0) 70%)',
          pointerEvents: 'none', filter: 'blur(40px)'
        }} />

        <Header />

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
          <Grid container spacing={4}>
            <Grid item xs={12}>
              <SystemStats />
            </Grid>
            <Grid item xs={12} md={7}>
              <PerformanceChart />
            </Grid>
            <Grid item xs={12} md={5}>
              <CommandTerminal />
            </Grid>
          </Grid>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
