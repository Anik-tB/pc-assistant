import React, { useState } from 'react';
import { Paper, Stack, Typography, TextField, IconButton, Box, CircularProgress, Fade, Avatar } from '@mui/material';
import { Terminal, Send, SmartToy, Person } from '@mui/icons-material';
import { useAppStore } from '../store/useAppStore';
import axios from 'axios';

export const CommandTerminal: React.FC = () => {
  const [input, setInput] = useState('');
  const { history, isProcessing, setProcessing, addHistoryItem } = useAppStore();

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;
    
    const userCmd = input;
    setInput('');
    addHistoryItem({ id: Date.now().toString(), role: 'user', content: userCmd, timestamp: new Date().toLocaleTimeString() });
    setProcessing(true);

    try {
      const response = await axios.post('/api/command/execute', { input: userCmd });
      addHistoryItem({
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: response.data.data?.message || JSON.stringify(response.data.data),
        timestamp: new Date().toLocaleTimeString()
      });
    } catch (error: any) {
      addHistoryItem({
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: `Error: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      });
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Fade in timeout={800}>
      <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Stack direction="row" alignItems="center" spacing={2} mb={2}>
          <Terminal sx={{ color: '#FF003C' }} />
          <Typography variant="h6" sx={{ letterSpacing: '0.05em' }}>
            AGENT TERMINAL
          </Typography>
        </Stack>

        <Box sx={{ 
          flexGrow: 1, 
          overflowY: 'auto', 
          mb: 2, 
          p: 2, 
          background: 'rgba(0,0,0,0.2)', 
          borderRadius: 2,
          border: '1px solid rgba(255,255,255,0.05)',
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}>
          {history.length === 0 && (
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 'auto', mb: 'auto', fontFamily: 'monospace' }}>
              System ready. Waiting for input...
            </Typography>
          )}
          {history.map((item) => (
            <Stack direction="row" spacing={2} key={item.id} sx={{ justifyContent: item.role === 'user' ? 'flex-end' : 'flex-start' }}>
              {item.role === 'agent' && (
                <Avatar sx={{ width: 28, height: 28, bgcolor: 'rgba(0, 240, 255, 0.1)', color: '#00F0FF', border: '1px solid rgba(0, 240, 255, 0.3)' }}>
                  <SmartToy sx={{ fontSize: 16 }} />
                </Avatar>
              )}
              <Box sx={{ 
                maxWidth: '80%', 
                p: 1.5, 
                borderRadius: 2, 
                background: item.role === 'user' ? 'rgba(0, 240, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                border: `1px solid ${item.role === 'user' ? 'rgba(0, 240, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)'}`,
              }}>
                <Typography variant="body2" sx={{ fontFamily: item.role === 'agent' ? 'monospace' : 'inherit', whiteSpace: 'pre-wrap' }}>
                  {item.content}
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', textAlign: 'right', mt: 1, opacity: 0.5 }}>
                  {item.timestamp}
                </Typography>
              </Box>
              {item.role === 'user' && (
                <Avatar sx={{ width: 28, height: 28, bgcolor: 'rgba(255, 0, 60, 0.1)', color: '#FF003C', border: '1px solid rgba(255, 0, 60, 0.3)' }}>
                  <Person sx={{ fontSize: 16 }} />
                </Avatar>
              )}
            </Stack>
          ))}
          {isProcessing && (
            <Stack direction="row" spacing={2} alignItems="center">
              <Avatar sx={{ width: 28, height: 28, bgcolor: 'rgba(0, 240, 255, 0.1)', color: '#00F0FF', border: '1px solid rgba(0, 240, 255, 0.3)' }}>
                <SmartToy sx={{ fontSize: 16 }} />
              </Avatar>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 1.5, borderRadius: 2, background: 'rgba(255, 255, 255, 0.05)' }}>
                <CircularProgress size={16} sx={{ color: '#00F0FF' }} />
                <Typography variant="body2" sx={{ fontFamily: 'monospace', color: '#00F0FF' }}>
                  Agent is thinking...
                </Typography>
              </Box>
            </Stack>
          )}
        </Box>

        <Stack direction="row" spacing={1}>
          <TextField
            fullWidth
            size="small"
            placeholder="Awaiting command..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            disabled={isProcessing}
            sx={{
              '& .MuiOutlinedInput-root': {
                fontFamily: 'monospace',
                background: 'rgba(0, 0, 0, 0.3)',
                '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.1)' },
                '&:hover fieldset': { borderColor: 'rgba(0, 240, 255, 0.5)' },
                '&.Mui-focused fieldset': { borderColor: '#00F0FF' }
              }
            }}
          />
          <IconButton 
            onClick={handleSend}
            disabled={isProcessing || !input.trim()}
            sx={{ 
              background: 'linear-gradient(135deg, #00F0FF 0%, #0080FF 100%)',
              color: '#070C16',
              borderRadius: 1,
              '&:hover': { background: '#5cffff' },
              '&.Mui-disabled': { background: 'rgba(255,255,255,0.1)' }
            }}
          >
            <Send />
          </IconButton>
        </Stack>
      </Paper>
    </Fade>
  );
};
