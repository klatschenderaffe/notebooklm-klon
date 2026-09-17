import { useEffect, useRef, useState } from 'react'
import type { Note, Source } from '../api'
import {
  addNote,
  addUrlSource,
  addYoutubeSource,
  deleteNote,
  deleteSource,
  listNotes,
  uploadSource,
} from '../api'

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

interface SourceNotesProps {
  notebookId: string
  sourceId: string
}

function SourceNotes({ notebookId, sourceId }: SourceNotesProps) {
  const [notes, setNotes] = useState<Note[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newNote, setNewNote] = useState('')
  const [isAdding, setIsAdding] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setIsLoading(true)
      try {
        const data = await listNotes(notebookId, sourceId)
        if (!cancelled) setNotes(data)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Notizen konnten nicht geladen werden')
        }
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [notebookId, sourceId])

  async function handleAddNote(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = newNote.trim()
    if (!trimmed || isAdding) return

    setError(null)
    setIsAdding(true)
    try {
      const note = await addNote(notebookId, sourceId, trimmed)
      setNotes((prev) => [...prev, note])
      setNewNote('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Notiz konnte nicht gespeichert werden')
    } finally {
      setIsAdding(false)
    }
  }

  async function handleDeleteNote(noteId: string) {
    try {
      await deleteNote(notebookId, sourceId, noteId)
      setNotes((prev) => prev.filter((note) => note.id !== noteId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Notiz konnte nicht gelöscht werden')
    }
  }

  return (
    <div className="source-notes">
      {isLoading && <p className="hint-text">Notizen werden geladen …</p>}
      {!isLoading && notes.length === 0 && <p className="hint-text">Noch keine Notizen</p>}
      {!isLoading && notes.length > 0 && (
        <ul className="note-list">
          {notes.map((note) => (
            <li key={note.id} className="note-item">
              <span className="note-content">{note.content}</span>
              <button
                type="button"
                className="icon-button"
                onClick={() => handleDeleteNote(note.id)}
                aria-label="Notiz löschen"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
      <form className="chat-input-row note-add-form" onSubmit={handleAddNote}>
        <input
          type="text"
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
          placeholder="Notiz hinzufügen …"
          disabled={isAdding}
        />
        <button type="submit" disabled={isAdding || !newNote.trim()}>
          {isAdding ? '…' : '+'}
        </button>
      </form>
      {error && <p className="error-text">{error}</p>}
    </div>
  )
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
  const [expandedSourceId, setExpandedSourceId] = useState<string | null>(null)

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
        {sources.map((source) => {
          const isExpanded = expandedSourceId === source.id
          return (
            <li key={source.id} className="source-list-item">
              <div className="source-item">
                <label className="source-checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedSourceIds.has(source.id)}
                    onChange={() => onToggleSource(source.id)}
                  />
                  <span className="source-type-badge">{TYPE_LABELS[source.file_type]}</span>
                  <span className="source-name">{source.filename}</span>
                </label>
                <div className="source-item-actions">
                  <button
                    type="button"
                    className="note-toggle-button"
                    onClick={() => setExpandedSourceId(isExpanded ? null : source.id)}
                    aria-expanded={isExpanded}
                  >
                    {isExpanded ? 'Notizen ▲' : 'Notizen ▾'}
                  </button>
                  <button
                    type="button"
                    className="icon-button"
                    onClick={() => handleDelete(source.id)}
                    aria-label={`${source.filename} löschen`}
                  >
                    ✕
                  </button>
                </div>
              </div>
              {isExpanded && <SourceNotes notebookId={notebookId} sourceId={source.id} />}
            </li>
          )
        })}
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
