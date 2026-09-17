import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import { listNotebooks, type Notebook } from '../api'
import { useAuth } from '../hooks/useAuth'

function DashboardPage() {
  const { user } = useAuth()
  const [notebooks, setNotebooks] = useState<Notebook[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listNotebooks()
      .then(setNotebooks)
      .catch((err) => setError(err instanceof Error ? err.message : 'Laden fehlgeschlagen'))
  }, [])

  const recent = notebooks.slice(0, 5)

  return (
    <>
      <AppHeader />
      <main className="app-main">
        <div className="dashboard">
          <h2>Willkommen{user?.email ? `, ${user.email}` : ''}</h2>
          <p className="hint-text">
            Du hast {notebooks.length} {notebooks.length === 1 ? 'Notebook' : 'Notebooks'}.
          </p>
          {error && <p className="error-text">{error}</p>}

          {recent.length > 0 && (
            <ul className="notebook-list">
              {recent.map((nb) => (
                <li key={nb.id} className="notebook-list-item">
                  <Link to={`/notebooks/${nb.id}`}>{nb.name}</Link>
                </li>
              ))}
            </ul>
          )}

          <Link to="/notebooks" className="dashboard-cta">
            Alle Notebooks ansehen →
          </Link>
        </div>
      </main>
    </>
  )
}

export default DashboardPage
