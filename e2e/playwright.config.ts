import { defineConfig } from '@playwright/test';

const API_BASE = process.env.API_BASE_URL ?? 'http://localhost:8000';
const UI_BASE = process.env.UI_BASE_URL ?? 'http://localhost:4200';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [['html', { open: 'never' }], ['list']],
  timeout: 30_000,
  expect: { timeout: 5_000 },

  projects: [
    {
      name: 'api',
      testDir: './tests/api',
      use: {
        baseURL: API_BASE,
        extraHTTPHeaders: { 'Content-Type': 'application/json' },
      },
    },
    {
      name: 'ui',
      testDir: './tests/ui',
      use: {
        baseURL: UI_BASE,
        browserName: 'chromium',
        headless: true,
      },
    },
  ],
});
