import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    // 0.0.0.0 lets the browser on the laptop reach the server inside the container.
    host: '0.0.0.0',
    port: 5173,
    // Every address starting with /api is forwarded to the backend container,
    // so the browser sees one address and no cross-origin setup is needed.
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    // jsdom gives a test a pretend browser: a document, a window and events.
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    // The stylesheet is not needed to check what a component puts on the page.
    css: false,
  },
})
