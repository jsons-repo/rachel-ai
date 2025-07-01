import { defineConfig } from 'vite';
import { FE_HOST, FE_PORT } from './src/sharedConfig';

export default defineConfig({
  server: {
    host: FE_HOST,
    port: FE_PORT,
    allowedHosts: ['rachel.local']
  },
});
