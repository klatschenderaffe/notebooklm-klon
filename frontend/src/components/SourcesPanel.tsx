import { useRef, useState } from 'react'
import type { Source } from '../api'
import { deleteSource, uploadSource } from '../api'

interface SourcesPanelProps {
  sources: Source[]
  selectedSourceIds: Set<string>
  onToggleSource: (id: string) => void
  onSourcesChange: () => void
}

function SourcesPanel({
  sources,
  selectedSourceIds,
  onToggleSource,
  onSourcesChange,
}: SourcesPanelProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleFiles(files: FileList | null) {
    const file = files?.[0]
    if (!file) return

    setError(null)
    setIsUploading(true)
    try {
      await uploadSource(file)
      onSourcesChange()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload fehlgeschlagen')
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteSource(id)
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
          accept=".pdf,.md,.markdown"
          onChange={(e) => handleFiles(e.target.files)}
          hidden
        />
        {isUploading ? 'Wird hochgeladen …' : 'Datei hierher ziehen oder klicken'}
      </label>
      <p className="filetypes">
        Unterstützte Dateitypen: <code>.pdf</code> <code>.md</code>
      </p>

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
