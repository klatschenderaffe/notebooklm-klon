import * as Sentry from '@sentry/react'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Nur aktiv, wenn ein DSN gesetzt ist -- ohne Sentry-Account/DSN ist das ein reines No-Op.
if (import.meta.env.VITE_SENTRY_DSN) {
  // Aktuell bewusst hoch (Standard 1.0 = 100%), da wir uns in der Staging-/Demo-Phase
  // ohne echten Produktivtraffic befinden. Bei echtem Produktivbetrieb sollte das auf
  // einen niedrigeren Wert (z.B. 0.1-0.2) reduziert werden, um im kostenlosen
  // Sentry-Kontingent (5.000.000 Spans/Monat) zu bleiben.
  const tracesSampleRate = Number(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE ?? 1.0)

  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || 'production',
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: Number.isFinite(tracesSampleRate) ? tracesSampleRate : 1.0,
  })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
