import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory.
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [react()],
    // Base public path when served in production
    base: '/',
    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: true, // Enable source maps for production
      rollupOptions: {
        output: {
          manualChunks: {
            // Split vendor and app code for better caching
            vendor: ['react', 'react-dom', 'react-router-dom'],
          },
        },
      },
      chunkSizeWarningLimit: 1600, // Size in KB
    },
    // Development server configuration
    server: {
      port: 3000,
      strictPort: true,
      open: true,
      proxy: {
        // Proxy API requests to your backend in development
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },
    // Resolve aliases for cleaner imports
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    // Environment variables
    define: {
      'process.env': {}
    }
  };
});
