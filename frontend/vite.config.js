import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/analyze': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/test-connection': 'http://127.0.0.1:8000',
    },
  },
})
