import React from 'react';
import { Grid, Card, CardContent, Typography, LinearProgress, Stack, Avatar, Zoom, Box } from '@mui/material';
import { Speed, Memory, Storage } from '@mui/icons-material';
import { useAppStore } from '../store/useAppStore';

const StatCard = ({ title, sub, value, icon, color1, color2, delay }: any) => {
  const getStatusColor = (val: number) => {
    if (val < 60) return '#00FF66'; // Green
    if (val < 85) return '#FFB300'; // Orange
    return '#FF003C'; // Red
  };

  const statusColor = getStatusColor(value);

  return (
    <Zoom in style={{ transitionDelay: `${delay}ms` }}>
      <Card sx={{
        position: 'relative',
        overflow: 'hidden',
        '&:hover': {
          transform: 'translateY(-5px)',
          boxShadow: `0 12px 40px rgba(${color1}, 0.2)`,
          borderColor: `rgba(${color1}, 0.4)`
        }
      }}>
        <Box sx={{
          position: 'absolute', top: 0, left: 0, width: '4px', height: '100%',
          background: `linear-gradient(to bottom, rgb(${color1}), rgb(${color2}))`
        }} />
        <CardContent sx={{ pl: 4 }}>
          <Stack direction="row" alignItems="center" spacing={2} mb={2}>
            <Avatar sx={{
              background: `linear-gradient(135deg, rgba(${color1},0.2) 0%, rgba(${color2},0.1) 100%)`,
              border: `1px solid rgba(${color1}, 0.5)`,
              color: `rgb(${color1})`
            }}>
              {icon}
            </Avatar>
            <Box>
              <Typography variant="h6" sx={{ letterSpacing: '0.05em' }}>{title}</Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                {sub}
              </Typography>
            </Box>
          </Stack>

          <Typography variant="h2" sx={{
            background: `linear-gradient(135deg, rgb(${color1}) 0%, rgb(${color2}) 100%)`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textShadow: `0 0 20px rgba(${color1}, 0.3)`
          }}>
            {value.toFixed(1)}%
          </Typography>

          <LinearProgress
            variant="determinate"
            value={value}
            sx={{
              mt: 2, height: 6, borderRadius: 3,
              backgroundColor: 'rgba(255,255,255,0.05)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 3,
                backgroundColor: statusColor,
                boxShadow: `0 0 10px ${statusColor}`
              }
            }}
          />
        </CardContent>
      </Card>
    </Zoom>
  );
};

export const SystemStats: React.FC = () => {
  const stats = useAppStore(state => state.stats);

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <StatCard 
          title="CPU CORE" sub="Processing Power" 
          value={stats.cpu_percent} icon={<Speed />} 
          color1="0, 240, 255" color2="0, 128, 255" delay={100} 
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <StatCard 
          title="MEMORY" sub={`${stats.ram_used_gb.toFixed(1)} / ${stats.ram_total_gb.toFixed(1)} GB`} 
          value={stats.ram_percent} icon={<Memory />} 
          color1="0, 255, 102" color2="0, 153, 51" delay={200} 
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <StatCard 
          title="STORAGE" sub={`${stats.disk_free_gb.toFixed(1)} GB FREE`} 
          value={stats.disk_percent} icon={<Storage />} 
          color1="255, 0, 60" color2="200, 0, 30" delay={300} 
        />
      </Grid>
    </Grid>
  );
};
