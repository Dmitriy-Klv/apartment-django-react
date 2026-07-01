import { Home } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'

const NAV_LINKS = [
  { label: 'Apartments', to: '/listings' },
  { label: 'How it works', to: '/how-it-works' },
  { label: 'Cities', to: '/cities' },
  { label: 'About', to: '/about' },
]

export function Navbar() {
  return (
    <header className="flex items-center justify-between px-2 py-4">
      <Link to="/" className="flex items-center gap-2 text-lg font-semibold tracking-tight">
        <span className="flex size-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <Home className="size-4" />
        </span>
        SoftStay
      </Link>

      <nav className="hidden items-center gap-8 text-sm font-medium text-muted-foreground md:flex">
        {NAV_LINKS.map((link) => (
          <Link key={link.to} to={link.to} className="transition-colors hover:text-foreground">
            {link.label}
          </Link>
        ))}
      </nav>

      <Button asChild size="lg" className="rounded-full px-5">
        <Link to="/register">Get started</Link>
      </Button>
    </header>
  )
}
