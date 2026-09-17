import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) return <p className="loading-text">Lädt …</p>
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default ProtectedRoute
