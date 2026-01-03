# Frontend Setup Guide

## Quick Start

### 1. Install Node.js Dependencies

```bash
cd frontend
npm install
```

This will install:
- React 18
- Material-UI (MUI)
- Recharts (for graphs)
- Socket.IO client (for WebSocket)
- Axios (for API calls)
- Vite (build tool)

### 2. Start the Development Server

```bash
npm run dev
```

The dashboard will be available at: **http://localhost:3000**

### 3. Start the Backend (Required!)

In another terminal:

```bash
cd ..
python -m uvicorn backend.main:app --reload
```

The backend API will run at: **http://localhost:8000**

## What You'll See

Once both servers are running, open http://localhost:3000 to see:

- **Real-time System Monitoring**
  - CPU usage graph
  - RAM usage
  - Disk usage

- **Command Interface**
  - Execute commands via web UI
  - See command history
  - Voice command button (future)

- **Live Updates**
  - WebSocket connection for real-time data
  - Auto-refreshing system stats every 5 seconds

## Troubleshooting

### "npm: command not found"
**Solution**: Install Node.js from https://nodejs.org/ (version 16 or higher)

### "Cannot connect to backend"
**Solution**: Make sure the backend is running:
```bash
python -m uvicorn backend.main:app --reload
```

### Port 3000 already in use
**Solution**: Change the port in `vite.config.ts`:
```typescript
server: {
  port: 3001,  // Change to any available port
  ...
}
```

### Dependencies installation fails
**Solution**: Clear npm cache and try again:
```bash
npm cache clean --force
npm install
```

## File Structure

```
frontend/
├── index.html          # HTML entry point
├── package.json        # Dependencies
├── vite.config.ts      # Vite configuration
├── tsconfig.json       # TypeScript config
├── src/
│   ├── main.tsx        # React entry point
│   └── App.tsx         # Main dashboard component
```

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- Frontend: Changes to `.tsx` files auto-refresh
- Backend: Changes to `.py` files auto-restart (with `--reload` flag)

### API Proxy
Vite is configured to proxy API requests:
- `/api/*` → `http://localhost:8000/api/*`
- `/ws` → `ws://localhost:8000/ws`

This means you can use relative URLs in your frontend code:
```typescript
axios.get('/api/system/status')  // No need for full URL
```

### Build for Production

```bash
npm run build
```

This creates optimized files in `dist/` folder.

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Start backend: `python -m uvicorn backend.main:app --reload`
3. ✅ Start frontend: `npm run dev`
4. ✅ Open browser: http://localhost:3000

Enjoy your web dashboard! 🎉
