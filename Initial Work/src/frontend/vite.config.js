import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// I keep the Vite config small because this frontend is still lightweight, but
// the dev proxy is important so frontend requests can reach the backend cleanly.
export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: true,
    target: 'es2020'
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true
      }
    }
  }
});
