import { createContext, useContext, useMemo, useState } from 'react'

import { logoutUser } from '@/api/auth'
import { clearSession, getRefreshToken, getStoredUser, saveSession } from '@/lib/authStorage'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser())

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      login: (session) => {
        saveSession(session)
        setUser(session.user)
      },
      logout: async () => {
        const refresh = getRefreshToken()
        if (refresh) {
          try {
            await logoutUser(refresh)
          } catch {}
        }
        clearSession()
        setUser(null)
      },
    }),
    [user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
