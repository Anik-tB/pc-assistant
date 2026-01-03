import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  IconButton,
  AppBar,
  Toolbar,
  Chip,
  Avatar,
  Fade,
  Slide,
  Zoom,
  Badge,
  Tooltip,
  Stack,
  Divider
} from '@mui/material';
import {
  Computer,
  Memory,
  Storage,
  Send,
  Mic,
  Settings,
  Speed,
  Timeline,
  Terminal,
  CloudQueue,
  Notifications,
  CheckCircle,
  Error as ErrorIcon
} from '@mui/icons-material';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';
import { io } from 'socket.io-client';
import axios from 'axios';

// TypeScript interfaces
interface SystemStats {
  cpu_percent: number;
  ram_percent: number;
  disk_percent: number;
  ram_used_gb: number;
  ram_total_gb: number;
  disk_free_gb: number;
}

interface CommandResult {
  success: boolean;
  message: string;
}

interface CommandHistoryItem {
  command: string;
  result: CommandResult;
  timestamp: string;
}

interface ChartDataPoint {
  time: string;
  cpu: number;
  ram: number;
}

function App() {
  const [systemStats, setSystemStats] = useState<SystemStats>({
    cpu_percent: 0,
    ram_percent: 0,
    disk_percent: 0,
    ram_used_gb: 0,
    ram_total_gb: 0,
    disk_free_gb: 0
  });

  const [command, setCommand] = useState<string>('');
  const [commandHistory, setCommandHistory] = useState<CommandHistoryItem[]>([]);
  const [cpuHistory, setCpuHistory] = useState<ChartDataPoint[]>([]);
  const [ramHistory, setRamHistory] = useState<any[]>([]);
  const [connected, setConnected] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  useEffect(() => {
    // Connect to WebSocket
    const socket = io('ws://localhost:8000');

    socket.on('connect', () => {
      setConnected(true);
      console.log('Connected to server');
    });

    socket.on('disconnect', () => {
      setConnected(false);
      console.log('Disconnected from server');
    });

    socket.on('system_status', (data) => {
      setSystemStats(data.data);

      const now = new Date();
      const timeStr = now.toLocaleTimeString();

      // Update CPU history
      setCpuHistory(prev => {
        const newHistory = [...prev, {
          time: timeStr,
          cpu: data.data.cpu_percent,
          ram: data.data.ram_percent
        }];
        return newHistory.slice(-30); // Keep last 30 points
      });

      // Update RAM history
      setRamHistory(prev => {
        const newHistory = [...prev, {
          time: timeStr,
          value: data.data.ram_percent
        }];
        return newHistory.slice(-30);
      });
    });

    socket.on('command_executed', (data) => {
      setCommandHistory(prev => [{
        command: data.command,
        result: data.result,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev].slice(0, 10));
      setIsProcessing(false);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const executeCommand = async () => {
    if (!command.trim()) return;

    setIsProcessing(true);
    try {
      const response = await axios.post('/api/command/execute', {
        input: command
      });

      setCommandHistory(prev => [{
        command: command,
        result: response.data.data,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev].slice(0, 10));

      setCommand('');
    } catch (error: any) {
      console.error('Error executing command:', error);
      setCommandHistory(prev => [{
        command: command,
        result: { success: false, message: 'Error: ' + (error?.message || 'Unknown error') },
        timestamp: new Date().toLocaleTimeString()
      }, ...prev].slice(0, 10));
    }
    setIsProcessing(false);
  };

  const getStatusColor = (percent: number): 'success' | 'warning' | 'error' => {
    if (percent < 50) return 'success';
    if (percent < 80) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a1929 0%, #1a2332 50%, #0a1929 100%)',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'radial-gradient(circle at 20% 50%, rgba(33, 150, 243, 0.1) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(245, 0, 87, 0.1) 0%, transparent 50%)',
        pointerEvents: 'none'
      }
    }}>
      {/* Animated Background Particles */}
      <Box sx={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
        opacity: 0.3
      }}>
        {[...Array(20)].map((_, i) => (
          <Box
            key={i}
            sx={{
              position: 'absolute',
              width: Math.random() * 4 + 2,
              height: Math.random() * 4 + 2,
              borderRadius: '50%',
              background: 'linear-gradient(45deg, #2196f3, #f50057)',
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animation: `float ${Math.random() * 10 + 10}s ease-in-out infinite`,
              '@keyframes float': {
                '0%, 100%': { transform: 'translateY(0px)' },
                '50%': { transform: `translateY(${Math.random() * 100 - 50}px)` }
              }
            }}
          />
        ))}
      </Box>

      {/* Modern AppBar */}
      <AppBar
        position="static"
        elevation={0}
        sx={{
          background: 'rgba(26, 35, 50, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}
      >
        <Toolbar>
          <Avatar sx={{
            mr: 2,
            background: 'linear-gradient(135deg, #2196f3 0%, #f50057 100%)',
            boxShadow: '0 0 20px rgba(33, 150, 243, 0.5)'
          }}>
            <Computer />
          </Avatar>
          <Typography variant="h5" component="div" sx={{
            flexGrow: 1,
            fontWeight: 700,
            background: 'linear-gradient(135deg, #2196f3 0%, #f50057 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            PC Automation Assistant
          </Typography>

          <Chip
            icon={<CloudQueue />}
            label={connected ? 'Connected' : 'Disconnected'}
            color={connected ? 'success' : 'error'}
            variant="outlined"
            sx={{
              mr: 2,
              backdropFilter: 'blur(10px)',
              background: connected ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)'
            }}
          />

          <Tooltip title="Notifications">
            <IconButton color="inherit">
              <Badge badgeContent={4} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>

          <Tooltip title="Settings">
            <IconButton color="inherit">
              <Settings />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, position: 'relative', zIndex: 1 }}>
        <Grid container spacing={3}>
          {/* System Stats Cards with Glassmorphism */}
          <Grid item xs={12} md={4}>
            <Zoom in timeout={300}>
              <Card sx={{
                background: 'rgba(26, 35, 50, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 12px 40px rgba(33, 150, 243, 0.3)',
                  border: '1px solid rgba(33, 150, 243, 0.3)'
                }
              }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                    <Avatar sx={{
                      background: 'linear-gradient(135deg, #2196f3 0%, #00bcd4 100%)',
                      boxShadow: '0 4px 20px rgba(33, 150, 243, 0.4)'
                    }}>
                      <Speed />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" fontWeight={600}>CPU Usage</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Processing Power
                      </Typography>
                    </Box>
                  </Stack>

                  <Typography variant="h2" fontWeight={700} sx={{
                    background: 'linear-gradient(135deg, #2196f3 0%, #00bcd4 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                  }}>
                    {systemStats.cpu_percent}%
                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={systemStats.cpu_percent}
                    color={getStatusColor(systemStats.cpu_percent)}
                    sx={{
                      mt: 2,
                      height: 8,
                      borderRadius: 4,
                      background: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                        background: 'linear-gradient(90deg, #2196f3 0%, #00bcd4 100%)'
                      }
                    }}
                  />
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          <Grid item xs={12} md={4}>
            <Zoom in timeout={400}>
              <Card sx={{
                background: 'rgba(26, 35, 50, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 12px 40px rgba(76, 175, 80, 0.3)',
                  border: '1px solid rgba(76, 175, 80, 0.3)'
                }
              }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                    <Avatar sx={{
                      background: 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
                      boxShadow: '0 4px 20px rgba(76, 175, 80, 0.4)'
                    }}>
                      <Memory />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" fontWeight={600}>RAM Usage</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {systemStats.ram_used_gb.toFixed(1)} / {systemStats.ram_total_gb.toFixed(1)} GB
                      </Typography>
                    </Box>
                  </Stack>

                  <Typography variant="h2" fontWeight={700} sx={{
                    background: 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                  }}>
                    {systemStats.ram_percent}%
                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={systemStats.ram_percent}
                    color={getStatusColor(systemStats.ram_percent)}
                    sx={{
                      mt: 2,
                      height: 8,
                      borderRadius: 4,
                      background: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                        background: 'linear-gradient(90deg, #4caf50 0%, #8bc34a 100%)'
                      }
                    }}
                  />
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          <Grid item xs={12} md={4}>
            <Zoom in timeout={500}>
              <Card sx={{
                background: 'rgba(26, 35, 50, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 12px 40px rgba(255, 152, 0, 0.3)',
                  border: '1px solid rgba(255, 152, 0, 0.3)'
                }
              }}>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2} mb={2}>
                    <Avatar sx={{
                      background: 'linear-gradient(135deg, #ff9800 0%, #ff5722 100%)',
                      boxShadow: '0 4px 20px rgba(255, 152, 0, 0.4)'
                    }}>
                      <Storage />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" fontWeight={600}>Disk Usage</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {systemStats.disk_free_gb.toFixed(1)} GB free
                      </Typography>
                    </Box>
                  </Stack>

                  <Typography variant="h2" fontWeight={700} sx={{
                    background: 'linear-gradient(135deg, #ff9800 0%, #ff5722 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                  }}>
                    {systemStats.disk_percent}%
                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={systemStats.disk_percent}
                    color={getStatusColor(systemStats.disk_percent)}
                    sx={{
                      mt: 2,
                      height: 8,
                      borderRadius: 4,
                      background: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                        background: 'linear-gradient(90deg, #ff9800 0%, #ff5722 100%)'
                      }
                    }}
                  />
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          {/* CPU & RAM History Chart */}
          <Grid item xs={12} md={8}>
            <Fade in timeout={600}>
              <Paper sx={{
                p: 3,
                background: 'rgba(26, 35, 50, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3
              }}>
                <Stack direction="row" alignItems="center" spacing={2} mb={3}>
                  <Timeline sx={{ color: '#2196f3' }} />
                  <Typography variant="h6" fontWeight={600}>
                    Performance Monitor
                  </Typography>
                  <Chip label="Live" color="success" size="small" sx={{ ml: 'auto' }} />
                </Stack>

                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={cpuHistory}>
                    <defs>
                      <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2196f3" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#2196f3" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorRam" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4caf50" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#4caf50" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="time" stroke="rgba(255,255,255,0.5)" />
                    <YAxis domain={[0, 100]} stroke="rgba(255,255,255,0.5)" />
                    <ChartTooltip
                      contentStyle={{
                        background: 'rgba(26, 35, 50, 0.95)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: 8
                      }}
                    />
                    <Area type="monotone" dataKey="cpu" stroke="#2196f3" fillOpacity={1} fill="url(#colorCpu)" strokeWidth={2} />
                    <Area type="monotone" dataKey="ram" stroke="#4caf50" fillOpacity={1} fill="url(#colorRam)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </Paper>
            </Fade>
          </Grid>

          {/* Command Interface */}
          <Grid item xs={12} md={4}>
            <Fade in timeout={700}>
              <Paper sx={{
                p: 3,
                background: 'rgba(26, 35, 50, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3,
                height: '100%'
              }}>
                <Stack direction="row" alignItems="center" spacing={2} mb={3}>
                  <Terminal sx={{ color: '#f50057' }} />
                  <Typography variant="h6" fontWeight={600}>
                    Command Center
                  </Typography>
                </Stack>

                <Stack spacing={2}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Enter command..."
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && executeCommand()}
                    disabled={isProcessing}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        background: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: 2,
                        '& fieldset': {
                          borderColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        '&:hover fieldset': {
                          borderColor: 'rgba(33, 150, 243, 0.5)'
                        }
                      }
                    }}
                  />

                  <Stack direction="row" spacing={1}>
                    <Button
                      fullWidth
                      variant="contained"
                      onClick={executeCommand}
                      disabled={isProcessing || !command.trim()}
                      startIcon={<Send />}
                      sx={{
                        background: 'linear-gradient(135deg, #2196f3 0%, #f50057 100%)',
                        borderRadius: 2,
                        textTransform: 'none',
                        fontWeight: 600,
                        '&:hover': {
                          background: 'linear-gradient(135deg, #1976d2 0%, #c51162 100%)',
                          transform: 'translateY(-2px)',
                          boxShadow: '0 8px 20px rgba(33, 150, 243, 0.4)'
                        }
                      }}
                    >
                      {isProcessing ? 'Processing...' : 'Execute'}
                    </Button>

                    <Tooltip title="Voice Command">
                      <IconButton
                        sx={{
                          background: 'rgba(245, 0, 87, 0.1)',
                          border: '1px solid rgba(245, 0, 87, 0.3)',
                          '&:hover': {
                            background: 'rgba(245, 0, 87, 0.2)'
                          }
                        }}
                      >
                        <Mic />
                      </IconButton>
                    </Tooltip>
                  </Stack>
                </Stack>

                <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

                <Typography variant="subtitle2" color="text.secondary" mb={1}>
                  Recent Commands
                </Typography>

                <List dense sx={{ maxHeight: 200, overflow: 'auto' }}>
                  {commandHistory.map((item, index) => (
                    <Slide direction="down" in key={index} timeout={300}>
                      <ListItem
                        sx={{
                          background: 'rgba(255, 255, 255, 0.03)',
                          borderRadius: 2,
                          mb: 1,
                          border: '1px solid rgba(255, 255, 255, 0.05)'
                        }}
                      >
                        <ListItemText
                          primary={
                            <Stack direction="row" alignItems="center" spacing={1}>
                              {item.result.success ?
                                <CheckCircle sx={{ fontSize: 16, color: '#4caf50' }} /> :
                                <ErrorIcon sx={{ fontSize: 16, color: '#f44336' }} />
                              }
                              <Typography variant="body2" fontWeight={500}>
                                {item.command}
                              </Typography>
                            </Stack>
                          }
                          secondary={
                            <Typography variant="caption" color="text.secondary">
                              {item.result.message} • {item.timestamp}
                            </Typography>
                          }
                        />
                      </ListItem>
                    </Slide>
                  ))}
                </List>
              </Paper>
            </Fade>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default App;
