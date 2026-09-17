import { useRef, useState } from 'react'
import type { Source } from '../api'
import { addUrlSource, addYoutubeSource, deleteSource, uploadSource } from '../api'

interface SourcesPanelProps {
  notebookId: string
  sources: Source[]
  selectedSourceIds: Set<string>
  onToggleSource: (id: string) => void
  onSourcesChange: () => void
}

const TYPE_LABELS: Record<Source['file_type'], string> = {
  pdf: 'PDF',
  md: 'MD',
  url: 'URL',
  youtube: 'YT',
  audio: 'Audio',
}

function SourcesPanel({
  notebookId,
  sources,
  selectedSourceIds,
  onToggleSource,
  onSourcesChange,
}: SourcesPanelProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [urlValue, setUrlValue] = useState('')
  const [isAddingUrl, setIsAddingUrl] = useState(false)
  const [youtubeValue, setYoutubeValue] = useState('')
  const [isAddingYoutube, setIsAddingYoutube] = useState(false)

  async function handleFiles(files: FileList | null) {
    const file = files?.[0]
    if (!file) return

    setError(null)
    setIsUploading(true)
    try {
      await uploadSource(notebookId, file)
      onSourcesChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload fehlgeschlagen')
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  async function handleAddUrl(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = urlValue.trim()
    if (!trimmed || isAddingUrl) return

    setError(null)
    setIsAddingUrl(true)
    try {
      await addUrlSource(notebookId, trimmed)
      setUrlValue('')
      onSourcesChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Webseite konnte nicht hinzugefügt werden')
    } finally {
      setIsAddingUrl(false)
    }
  }

  async function handleAddYoutube(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = youtubeValue.trim()
    if (!trimmed || isAddingYoutube) return

    setError(null)
    setIsAddingYoutube(true)
    try {
      await addYoutubeSource(notebookId, trimmed)
      setYoutubeValue('')
      onSourcesChange()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'YouTube-Transkript konnte nicht abgerufen werden'
      )
    } finally {
      setIsAddingYoutube(false)
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteSource(notebookId, id)
      onSourcesChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Löschen fehlgeschlagen')
    }
  }

  return (
    <section className="panel sources-panel">
      <h2>Quellen</h2>

      <label
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault()
          handleFiles(e.dataTransfer.files)
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.md,.markdown,.mp3,.wav,.m4a,.ogg"
          onChange={(e) => handleFiles(e.target.files)}
          hidden
        />
        {isUploading ? 'Wird hochgeladen …' : 'Datei hierher ziehen oder klicken'}
      </label>
      <p className="filetypes">
        Unterstützte Dateitypen: <code>.pdf</code> <code>.md</code> <code>.mp3</code>{' '}
        <code>.wav</code> <code>.m4a</code> <code>.ogg</code>
      </p>

      <form className="chat-input-row source-add-form" onSubmit={handleAddUrl}>
        <input
          type="text"
          value={urlValue}
          onChange={(e) => setUrlValue(e.target.value)}
          placeholder="Webseiten-URL einfügen …"
          disabled={isAddingUrl}
        />
        <button type="submit" disabled={isAddingUrl || !urlValue.trim()}>
          {isAddingUrl ? '…' : '+'}
        </button>
      </form>

      <form className="chat-input-row source-add-form" onSubmit={handleAddYoutube}>
        <input
          type="text"
          value={youtubeValue}
          onChange={(e) => setYoutubeValue(e.target.value)}
          placeholder="YouTube-Link einfügen …"
          disabled={isAddingYoutube}
        />
        <button type="submit" disabled={isAddingYoutube || !youtubeValue.trim()}>
          {isAddingYoutube ? '…' : '+'}
        </button>
      </form>

      {error && <p className="error-text">{error}</p>}

      <ul className="source-list">
        {sources.map((source) => (
          <li key={source.id} className="source-item">
            <label className="source-checkbox-label">
              <input
                type="checkbox"
                checked={selectedSourceIds.has(source.id)}
                onChange={() => onToggleSource(source.id)}
              />
              <span className="source-type-badge">{TYPE_LABELS[source.file_type]}</span>
              <span className="source-name">{source.filename}</span>
            </label>
            <button
              type="button"
              className="icon-button"
              onClick={() => handleDelete(source.id)}
              aria-label={`${source.filename} löschen`}
            >
              ✕
            </button>
          </li>
        ))}
        {sources.length === 0 && <li className="source-empty">Noch keine Quellen hochgeladen</li>}
      </ul>
      {sources.length > 0 && (
        <p className="hint-text">
          Abgewählte Quellen werden bei der Präsentationserstellung nicht berücksichtigt.
        </p>
      )}
    </section>
  )
}

export default SourcesPanel
