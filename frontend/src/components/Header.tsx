import React from 'react';
import { AppBar, Toolbar, Typography, Avatar, Chip, Tooltip, IconButton, Badge } from '@mui/material';
import { Computer, CloudQueue, Notifications, Settings } from '@mui/icons-material';
import { useAppStore } from '../store/useAppStore';

export const Header: React.FC = () => {
  const connected = useAppStore(state => state.connected);

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        background: 'rgba(11, 20, 38, 0.4)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(0, 240, 255, 0.1)'
      }}
    >
      <Toolbar>
        <Avatar sx={{
          mr: 2,
          background: 'linear-gradient(135deg, #00F0FF 0%, #0080FF 100%)',
          boxShadow: '0 0 20px rgba(0, 240, 255, 0.5)'
        }}>
          <Computer sx={{ color: '#070C16' }} />
        </Avatar>
        <Typography variant="h5" component="div" sx={{
          flexGrow: 1,
          fontWeight: 800,
          background: 'linear-gradient(135deg, #00F0FF 0%, #FF003C 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: '-0.02em'
        }}>
          NEXUS ASSISTANT
        </Typography>

        <Chip
          icon={<CloudQueue />}
          label={connected ? 'LINK ESTABLISHED' : 'OFFLINE'}
          color={connected ? 'success' : 'error'}
          variant="outlined"
          sx={{
            mr: 2,
            fontWeight: 700,
            letterSpacing: '0.05em',
            backdropFilter: 'blur(10px)',
            borderWidth: 2,
            background: connected ? 'rgba(0, 255, 102, 0.1)' : 'rgba(255, 0, 60, 0.1)',
            borderColor: connected ? 'rgba(0, 255, 102, 0.5)' : 'rgba(255, 0, 60, 0.5)',
            color: connected ? '#00FF66' : '#FF003C',
            '& .MuiChip-icon': {
              color: connected ? '#00FF66' : '#FF003C',
            }
          }}
        />

        <Tooltip title="System Alerts">
          <IconButton color="inherit" sx={{ '&:hover': { color: '#00F0FF' } }}>
            <Badge badgeContent={0} color="secondary">
              <Notifications />
            </Badge>
          </IconButton>
        </Tooltip>

        <Tooltip title="Configuration">
          <IconButton color="inherit" sx={{ '&:hover': { color: '#00F0FF' } }}>
            <Settings />
          </IconButton>
        </Tooltip>
      </Toolbar>
    </AppBar>
  );
};
