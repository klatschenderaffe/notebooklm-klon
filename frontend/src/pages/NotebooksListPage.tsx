import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import {
  createNotebook,
  deleteNotebook,
  listNotebooks,
  renameNotebook,
  type Notebook,
} from '../api'

function NotebooksListPage() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([])
  const [newName, setNewName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  function refresh() {
    listNotebooks()
      .then(setNotebooks)
      .catch((err) => setError(err instanceof Error ? err.message : 'Laden fehlgeschlagen'))
  }

  useEffect(refresh, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = newName.trim()
    if (!trimmed || isCreating) return
    setIsCreating(true)
    try {
      await createNotebook(trimmed)
      setNewName('')
      refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erstellen fehlgeschlagen')
    } finally {
      setIsCreating(false)
    }
  }

  async function handleRename(nb: Notebook) {
    const name = window.prompt('Neuer Name für das Notebook:', nb.name)
    if (!name || !name.trim() || name.trim() === nb.name) return
    try {
      await renameNotebook(nb.id, name.trim())
      refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Umbenennen fehlgeschlagen')
    }
  }

  async function handleDelete(nb: Notebook) {
    if (!window.confirm(`"${nb.name}" inkl. aller Quellen unwiderruflich löschen?`)) return
    try {
      await deleteNotebook(nb.id)
      refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Löschen fehlgeschlagen')
    }
  }

  return (
    <>
      <AppHeader />
      <main className="app-main">
        <div className="notebooks-page">
          <h2>Deine Notebooks</h2>

          <form onSubmit={handleCreate} className="presentation-form">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Name des neuen Notebooks …"
              disabled={isCreating}
            />
            <button type="submit" disabled={isCreating || !newName.trim()}>
              {isCreating ? 'Wird erstellt …' : 'Notebook erstellen'}
            </button>
          </form>

          {error && <p className="error-text">{error}</p>}

          <ul className="notebook-list">
            {notebooks.map((nb) => (
              <li key={nb.id} className="notebook-list-item">
                <Link to={`/notebooks/${nb.id}`}>{nb.name}</Link>
                <div className="notebook-actions">
                  <button type="button" className="icon-button" onClick={() => handleRename(nb)}>
                    ✎
                  </button>
                  <button type="button" className="icon-button" onClick={() => handleDelete(nb)}>
                    ✕
                  </button>
                </div>
              </li>
            ))}
            {notebooks.length === 0 && (
              <li className="source-empty">Noch keine Notebooks — leg dein erstes an.</li>
            )}
          </ul>
        </div>
      </main>
    </>
  )
}

export default NotebooksListPage
