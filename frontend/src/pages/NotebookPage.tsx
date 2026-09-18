import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import ChatPanel from '../components/ChatPanel'
import PresentationHistoryPanel from '../components/PresentationHistoryPanel'
import PresentationPanel from '../components/PresentationPanel'
import SourcesPanel from '../components/SourcesPanel'
import { listSources, type Source } from '../api'

function NotebookPage() {
  const { notebookId } = useParams<{ notebookId: string }>()
  const [sources, setSources] = useState<Source[]>([])
  const [selectedSourceIds, setSelectedSourceIds] = useState<Set<string>>(new Set())
  const [loadError, setLoadError] = useState<string | null>(null)
  const [presentationRefreshKey, setPresentationRefreshKey] = useState(0)
  const leftColumnRef = useRef<HTMLDivElement>(null)
  const [leftColumnHeight, setLeftColumnHeight] = useState<number | null>(null)

  // Reines CSS kann die Höhe der linken Spalte nicht gleichzeitig als Vorgabe UND als
  // Obergrenze für das (potenziell viel längere) Chat-Panel nutzen -- ein Grid-Element
  // mit unbegrenztem eigenen Inhalt bläht die automatische Zeilenhöhe trotz
  // min-height:0/overflow:hidden auf. Deshalb wird die Höhe hier gemessen und per
  // CSS-Variable an das Chat-Panel weitergereicht (siehe .chat-panel in App.css).
  useEffect(() => {
    const el = leftColumnRef.current
    if (!el) return
    const observer = new ResizeObserver((entries) => {
      setLeftColumnHeight(entries[0].contentRect.height)
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

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
          <div className="layout-column" ref={leftColumnRef}>
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
              onPresentationCreated={() => setPresentationRefreshKey((k) => k + 1)}
            />
            <PresentationHistoryPanel
              notebookId={notebookId}
              refreshKey={presentationRefreshKey}
            />
          </div>
          <div
            className="chat-panel-slot"
            style={
              leftColumnHeight
                ? ({ '--chat-panel-match-height': `${leftColumnHeight}px` } as React.CSSProperties)
                : undefined
            }
          >
            <ChatPanel notebookId={notebookId} hasSources={sources.length > 0} />
          </div>
        </div>
      </main>
    </>
  )
}

export default NotebookPage
