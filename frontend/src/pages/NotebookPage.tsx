import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import ChatPanel from '../components/ChatPanel'
import PresentationPanel from '../components/PresentationPanel'
import SourcesPanel from '../components/SourcesPanel'
import { listSources, type Source } from '../api'

function NotebookPage() {
  const { notebookId } = useParams<{ notebookId: string }>()
  const [sources, setSources] = useState<Source[]>([])
  const [selectedSourceIds, setSelectedSourceIds] = useState<Set<string>>(new Set())
  const [loadError, setLoadError] = useState<string | null>(null)

  const refreshSources = useCallback(() => {
    if (!notebookId) return
    listSources(notebookId)
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
  }, [notebookId])

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

  if (!notebookId) return null

  return (
    <>
      <AppHeader />
      <main className="app-main">
        <Link to="/notebooks" className="back-link">
          ← Zu allen Notebooks
        </Link>
        {loadError && <p className="error-text banner">{loadError}</p>}
        <div className="layout">
          <div className="layout-column">
            <SourcesPanel
              notebookId={notebookId}
              sources={sources}
              selectedSourceIds={selectedSourceIds}
              onToggleSource={toggleSource}
              onSourcesChange={refreshSources}
            />
            <PresentationPanel
              notebookId={notebookId}
              hasSources={sources.length > 0}
              selectedSourceIds={[...selectedSourceIds]}
            />
          </div>
          <ChatPanel notebookId={notebookId} hasSources={sources.length > 0} />
        </div>
      </main>
    </>
  )
}

export default NotebookPage
