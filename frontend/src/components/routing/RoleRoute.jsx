import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'

export function RoleRoute({ role }) {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (user.role !== role) {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
