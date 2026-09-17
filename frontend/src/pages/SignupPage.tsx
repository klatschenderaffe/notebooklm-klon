import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import AppHeader from '../components/AppHeader'
import { useAuth } from '../hooks/useAuth'

function SignupPage() {
  const { user, signUp } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (user) return <Navigate to="/dashboard" replace />

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)
    const { error } = await signUp(email, password)
    setIsSubmitting(false)
    if (error) setError(error)
    else setSuccess(true)
  }

  return (
    <>
      <AppHeader />
      <main className="app-main">
        <div className="auth-card">
          <h2>Konto erstellen</h2>
          {success ? (
            <p className="hint-text">
              Fast geschafft — bitte bestätige deine E-Mail-Adresse über den Link, den wir dir
              geschickt haben, und melde dich anschließend an.
            </p>
          ) : (
            <>
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
                  placeholder="Passwort (mind. 6 Zeichen)"
                  autoComplete="new-password"
                  minLength={6}
                  required
                />
                <button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Wird erstellt …' : 'Registrieren'}
                </button>
              </form>
              {error && <p className="error-text">{error}</p>}
            </>
          )}
          <p className="hint-text">
            Bereits ein Konto? <Link to="/login">Anmelden</Link>
          </p>
        </div>
      </main>
    </>
  )
}

export default SignupPage
