import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { listSources, type Source } from './api'
import ChatPanel from './components/ChatPanel'
import PresentationPanel from './components/PresentationPanel'
import SourcesPanel from './components/SourcesPanel'

type Theme = 'light' | 'dark'

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('theme')
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const [sources, setSources] = useState<Source[]>([])
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const refreshSources = useCallback(() => {
    listSources()
      .then(setSources)
      .catch((err) => setLoadError(err instanceof Error ? err.message : 'Laden fehlgeschlagen'))
  }, [])

  useEffect(() => {
    refreshSources()
  }, [refreshSources])

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
        {loadError && <p className="error-text banner">{loadError}</p>}
        <div className="layout">
          <div className="layout-column">
            <SourcesPanel sources={sources} onSourcesChange={refreshSources} />
            <PresentationPanel hasSources={sources.length > 0} />
          </div>
          <ChatPanel hasSources={sources.length > 0} />
        </div>
      </main>
    </>
  )
}

export default App
