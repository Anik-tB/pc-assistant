import React from 'react';
import { Paper, Stack, Typography, Chip, Fade } from '@mui/material';
import { Timeline } from '@mui/icons-material';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer } from 'recharts';
import { useAppStore } from '../store/useAppStore';

export const PerformanceChart: React.FC = () => {
  const cpuHistory = useAppStore(state => state.cpuHistory);

  return (
    <Fade in timeout={600}>
      <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Stack direction="row" alignItems="center" spacing={2} mb={3}>
          <Timeline sx={{ color: '#00F0FF' }} />
          <Typography variant="h6" sx={{ letterSpacing: '0.05em' }}>
            TELEMETRY DATA
          </Typography>
          <Chip label="LIVE" size="small" sx={{ 
            ml: 'auto', 
            background: 'rgba(0, 240, 255, 0.1)', 
            color: '#00F0FF',
            border: '1px solid rgba(0, 240, 255, 0.3)'
          }} />
        </Stack>

        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={cpuHistory} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.5} />
                <stop offset="95%" stopColor="#00F0FF" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorRam" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00FF66" stopOpacity={0.5} />
                <stop offset="95%" stopColor="#00FF66" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} />
            <YAxis domain={[0, 100]} stroke="rgba(255,255,255,0.3)" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} />
            <ChartTooltip
              contentStyle={{
                background: 'rgba(11, 20, 38, 0.95)',
                border: '1px solid rgba(0, 240, 255, 0.3)',
                borderRadius: 8,
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)'
              }}
              itemStyle={{ color: '#fff' }}
            />
            <Area type="monotone" dataKey="cpu" name="CPU" stroke="#00F0FF" fill="url(#colorCpu)" strokeWidth={2} />
            <Area type="monotone" dataKey="ram" name="RAM" stroke="#00FF66" fill="url(#colorRam)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </Paper>
    </Fade>
  );
};
