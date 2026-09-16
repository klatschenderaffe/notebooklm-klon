import { useEffect, useState } from 'react'
import './App.css'

type Theme = 'light' | 'dark'
type BackendStatus = 'pending' | 'ok' | 'error'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('theme')
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('pending')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => (res.ok ? setBackendStatus('ok') : setBackendStatus('error')))
      .catch(() => setBackendStatus('error'))
  }, [])

  const statusLabel: Record<BackendStatus, string> = {
    pending: 'Prüfe Backend-Verbindung …',
    ok: 'Backend erreichbar',
    error: 'Backend nicht erreichbar',
  }

  return (
    <>
      <header className="app-header">
        <h1 className="app-title">NotebookLM-Klon</h1>
        <button
          type="button"
          className="theme-toggle"
          onClick={() => setTheme((t) => (t === 'light' ? 'dark' : 'light'))}
        >
          {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
        </button>
      </header>

      <main className="app-main">
        <div className="upload-card">
          <h2>Dateien hochladen</h2>
          <p className="subtitle">
            Lade deine Quellen hoch und stelle anschließend Fragen dazu — die KI antwortet
            ausschließlich auf Basis dieser Dateien.
          </p>
          <div className="dropzone">Datei-Upload folgt in einem späteren Schritt</div>
          <p className="filetypes">
            Unterstützte Dateitypen: <code>.pdf</code> <code>.md</code>
          </p>
          <p className="status-line">
            <span className={`status-dot ${backendStatus}`} />
            {statusLabel[backendStatus]}
          </p>
        </div>
      </main>
    </>
  )
}

export default App
