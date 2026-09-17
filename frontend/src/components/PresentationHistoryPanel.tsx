import { useEffect, useState } from 'react'
import { downloadPresentation, listPresentationHistory, type PresentationHistoryItem } from '../api'

interface PresentationHistoryPanelProps {
  notebookId: string
  refreshKey: number
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function PresentationHistoryPanel({ notebookId, refreshKey }: PresentationHistoryPanelProps) {
  const [items, setItems] = useState<PresentationHistoryItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [downloadingId, setDownloadingId] = useState<string | null>(null)

  useEffect(() => {
    listPresentationHistory(notebookId)
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : 'Laden fehlgeschlagen'))
  }, [notebookId, refreshKey])

  async function handleDownload(item: PresentationHistoryItem) {
    setDownloadingId(item.id)
    setError(null)
    try {
      const blob = await downloadPresentation(notebookId, item.id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${item.title}.pptx`
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download fehlgeschlagen')
    } finally {
      setDownloadingId(null)
    }
  }

  if (items.length === 0 && !error) return null

  return (
    <section className="panel">
      <h2>Frühere Präsentationen</h2>
      {error && <p className="error-text">{error}</p>}
      <ul className="notebook-list">
        {items.map((item) => (
          <li key={item.id} className="notebook-list-item">
            <span className="source-name">
              {item.title}
              <span className="hint-text"> · {formatDate(item.created_at)}</span>
            </span>
            <button
              type="button"
              className="icon-button"
              onClick={() => handleDownload(item)}
              disabled={downloadingId === item.id}
              aria-label={`${item.title} herunterladen`}
            >
              {downloadingId === item.id ? '…' : '↓'}
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}

export default PresentationHistoryPanel
