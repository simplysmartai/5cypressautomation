import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://www.5cypress.com',
  integrations: [sitemap()],
  output: 'static',
  vite: {
    server: {
      proxy: {
        // Proxy API calls to Express server during local dev
        '/api': 'http://localhost:3000',
      },
    },
  },
});
