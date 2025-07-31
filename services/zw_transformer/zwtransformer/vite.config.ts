import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: '.',
  build: {
    rollupOptions: {
      input: './index.html'
    }
  },
  server: {
    watch: {
      ignored: [
        '**/tenlabs-env/**',
        '**/venv/**',
        '**/node_modules/**',
        '**/.git/**',
        '**/backend/**',
        '**/*.wav',
        '**/*.onnx',
        '**/__pycache__/**',
        '**/site-packages/**',
        '**/lib/**',
        '**/lib64/**'
      ]
    }
  }
})
