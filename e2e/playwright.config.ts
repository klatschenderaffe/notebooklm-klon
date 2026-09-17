import { defineConfig, devices } from '@playwright/test'

/**
 * E2E-Smoke-Tests für den NotebookLM-Klon.
 * Laufen bewusst OHNE echte Supabase/Gemini-Credentials -- geprüft wird nur
 * clientseitiges Verhalten (Formulare, Routing), keine echten Backend-Calls.
 *
 * Lokal: `E2E_BASE_URL` optional setzen, Default ist der lokale Vite-Dev-Server.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
