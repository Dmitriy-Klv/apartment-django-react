import { Home, LogOut, User } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { useAuth } from '@/context/AuthContext'

const BASE_LINKS = [
  { label: 'Apartments', to: '/listings' },
  { label: 'About', to: '/about' },
  { label: 'Contact', to: '/contact' },
]

const ROLE_LINKS = {
  tenant: [{ label: 'My bookings', to: '/my-bookings' }],
  lessor: [
    { label: 'My listings', to: '/my-listings' },
    { label: 'Bookings', to: '/lessor/bookings' },
  ],
}

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const navLinks = [...BASE_LINKS, ...(user ? ROLE_LINKS[user.role] || [] : [])]

  return (
    <header className="flex items-center justify-between px-2 py-4">
      <Link to="/" className="flex items-center gap-2 text-lg font-semibold tracking-tight">
        <span className="flex size-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <Home className="size-4" />
        </span>
        SoftStay
      </Link>

      <nav className="hidden items-center gap-8 text-sm font-medium text-muted-foreground md:flex">
        {navLinks.map((link) => (
          <Link key={link.to} to={link.to} className="transition-colors hover:text-foreground">
            {link.label}
          </Link>
        ))}
      </nav>

      {isAuthenticated ? (
        <div className="flex items-center gap-2">
          <Button asChild variant="ghost" size="lg" className="gap-2 rounded-full px-4">
            <Link to="/profile">
              <User className="size-4" />
              {user.first_name}
            </Link>
          </Button>
          <Button variant="outline" size="lg" className="gap-2 rounded-full px-4" onClick={logout}>
            <LogOut className="size-4" />
            Log out
          </Button>
        </div>
      ) : (
        <div className="flex items-center gap-2">
          <Button asChild variant="ghost" size="lg" className="rounded-full px-4">
            <Link to="/login">Sign in</Link>
          </Button>
          <Button asChild size="lg" className="rounded-full px-5">
            <Link to="/register">Get started</Link>
          </Button>
        </div>
      )}
    </header>
  )
}
