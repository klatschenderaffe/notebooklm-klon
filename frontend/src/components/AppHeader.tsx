import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

type Theme = 'light' | 'dark'

function getInitialTheme(): Theme {
  const stored = localStorage.getItem('theme')
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function AppHeader() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const { user, signOut } = useAuth()

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  return (
    <header className="app-header">
      <div className="app-header-left">
        <Link to="/dashboard" className="app-title">
          NotebookLM-Klon
        </Link>
        {user && (
          <nav className="app-nav">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/notebooks">Notebooks</Link>
          </nav>
        )}
      </div>
      <div className="app-header-right">
        <button
          type="button"
          className="theme-toggle"
          onClick={() => setTheme((t) => (t === 'light' ? 'dark' : 'light'))}
        >
          {theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode'}
        </button>
        {user && (
          <button type="button" className="theme-toggle" onClick={() => signOut()}>
            Abmelden
          </button>
        )}
      </div>
    </header>
  )
}

export default AppHeader
