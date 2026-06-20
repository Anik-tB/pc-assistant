import { create } from 'zustand';
// Removed socket.io-client import

export interface SystemStats {
  cpu_percent: number;
  ram_percent: number;
  disk_percent: number;
  ram_used_gb: number;
  ram_total_gb: number;
  disk_free_gb: number;
}

export interface CommandResult {
  success: boolean;
  message: string;
  output?: string;
  data?: any;
}

export interface CommandHistoryItem {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
  isThinking?: boolean;
}

export interface ChartDataPoint {
  time: string;
  cpu: number;
  ram: number;
}

interface AppState {
  // Connection
  connected: boolean;
  socket: WebSocket | null;
  connect: () => void;
  disconnect: () => void;

  // System Stats
  stats: SystemStats;
  cpuHistory: ChartDataPoint[];
  
  // Agent Chat / Command History
  history: CommandHistoryItem[];
  isProcessing: boolean;
  
  // Actions
  setProcessing: (val: boolean) => void;
  addHistoryItem: (item: CommandHistoryItem) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  connected: false,
  socket: null,
  
  stats: {
    cpu_percent: 0,
    ram_percent: 0,
    disk_percent: 0,
    ram_used_gb: 0,
    ram_total_gb: 0,
    disk_free_gb: 0
  },
  cpuHistory: [],
  
  history: [],
  isProcessing: false,

  setProcessing: (val) => set({ isProcessing: val }),
  addHistoryItem: (item) => set((state) => ({ 
    history: [...state.history, item] 
  })),

  connect: () => {
    if (get().socket) return;
    
    const socket = new WebSocket('ws://localhost:8000/ws');
    
    socket.onopen = () => {
      set({ connected: true });
    };

    socket.onclose = () => {
      set({ connected: false });
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'system_status') {
          const data = message.data;
          const timeStr = new Date().toLocaleTimeString();
          set((state) => {
            const newHistory = [...state.cpuHistory, {
              time: timeStr,
              cpu: data.cpu_percent,
              ram: data.ram_percent
            }];
            return {
              stats: data,
              cpuHistory: newHistory.slice(-30)
            };
          });
        }
      } catch (err) {
        console.error('Failed to parse websocket message', err);
      }
    };

    set({ socket });
  },

  disconnect: () => {
    const { socket } = get();
    if (socket) {
      socket.close();
      set({ socket: null, connected: false });
    }
  }
}));
