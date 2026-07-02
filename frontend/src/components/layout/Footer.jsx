import { Link } from 'react-router-dom'

export function Footer() {
  return (
    <footer className="flex flex-col gap-4 border-t border-border py-8 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
      <p>© {new Date().getFullYear()} SoftStay. All rights reserved.</p>
      <div className="flex gap-6">
        <Link to="/privacy" className="transition-colors hover:text-foreground">
          Privacy policy
        </Link>
        <Link to="/terms" className="transition-colors hover:text-foreground">
          Terms of service
        </Link>
        <Link to="/contact" className="transition-colors hover:text-foreground">
          Contact
        </Link>
        <Link to="/impressum" className="transition-colors hover:text-foreground">
          Legal notice
        </Link>
      </div>
    </footer>
  )
}
