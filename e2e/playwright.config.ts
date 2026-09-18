import { defineConfig, devices } from '@playwright/test'

/**
 * E2E-Smoke-Tests für den NotebookLM-Klon.
 * Laufen standardmäßig gegen die echte, live deployte Staging-Umgebung
 * (E2E_BASE_URL in CI). Die meisten Tests prüfen nur clientseitiges Verhalten
 * (Formulare, Routing) ohne echten Backend-Call; ein Test führt bewusst einen
 * echten Login gegen Staging durch, um die komplette Kette zu verifizieren.
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
      // Der '@staging'-Test (echter Login mit echtem Passwort gegen Staging)
      // läuft in einem eigenen Projekt weiter unten, das Tracing deaktiviert --
      // hier ausschließen, damit er nicht zusätzlich mit Tracing an läuft.
      grepInvert: /@staging/,
    },
    {
      // Eigenes Projekt nur für den echten Staging-Login-Test, damit Tracing
      // dafür deaktiviert werden kann (test.use({ trace }) direkt in einer
      // describe-Gruppe verbietet Playwright, siehe Kommentar in auth.spec.ts).
      // Grund: der Test tippt ein echtes Klartext-Passwort per .fill() ein, das
      // sonst in einem Trace-Artifact landen könnte.
      name: 'chromium-staging',
      use: { ...devices['Desktop Chrome'], trace: 'off' },
      grep: /@staging/,
    },
  ],
})
