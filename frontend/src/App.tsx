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
  const [selectedSourceIds, setSelectedSourceIds] = useState<Set<string>>(new Set())
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const refreshSources = useCallback(() => {
    listSources()
      .then((newSources) => {
        setSources(newSources)
        setSelectedSourceIds((prev) => {
          const validIds = new Set(newSources.map((s) => s.id))
          const next = new Set([...prev].filter((id) => validIds.has(id)))
          for (const s of newSources) {
            if (!prev.has(s.id)) next.add(s.id)
          }
          return next
        })
      })
      .catch((err) => setLoadError(err instanceof Error ? err.message : 'Laden fehlgeschlagen'))
  }, [])

  useEffect(() => {
    refreshSources()
  }, [refreshSources])

  function toggleSource(id: string) {
    setSelectedSourceIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
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
        {loadError && <p className="error-text banner">{loadError}</p>}
        <div className="layout">
          <div className="layout-column">
            <SourcesPanel
              sources={sources}
              selectedSourceIds={selectedSourceIds}
              onToggleSource={toggleSource}
              onSourcesChange={refreshSources}
            />
            <PresentationPanel
              hasSources={sources.length > 0}
              selectedSourceIds={[...selectedSourceIds]}
            />
          </div>
          <ChatPanel hasSources={sources.length > 0} />
        </div>
      </main>
    </>
  )
}

export default App
