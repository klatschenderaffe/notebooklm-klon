import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import { useAuth } from '../hooks/useAuth'

function LoginPage() {
  const { user, signIn } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (user) return <Navigate to="/dashboard" replace />

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    const { error } = await signIn(email, password)
    setIsSubmitting(false)
    if (error) setError(error)
    else navigate('/dashboard')
  }

  return (
    <>
      <AppHeader />
      <main className="app-main">
        <div className="auth-card">
          <h2>Anmelden</h2>
          <form onSubmit={handleSubmit} className="auth-form">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="E-Mail"
              autoComplete="email"
              required
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Passwort"
              autoComplete="current-password"
              required
            />
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Wird angemeldet …' : 'Anmelden'}
            </button>
          </form>
          {error && <p className="error-text">{error}</p>}
          <p className="hint-text">
            Noch kein Konto? <Link to="/signup">Registrieren</Link>
          </p>
        </div>
      </main>
    </>
  )
}

export default LoginPage
