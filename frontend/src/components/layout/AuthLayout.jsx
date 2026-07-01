import { Home } from 'lucide-react'
import { Link } from 'react-router-dom'

import { IMAGES } from '@/lib/images'

export function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <div className="relative hidden md:block">
        <img src={IMAGES.heroVilla} alt="Modern villa exterior" className="h-full w-full object-cover" />
        <div className="absolute inset-0 bg-black/30" />
        <Link to="/" className="absolute left-8 top-8 flex items-center gap-2 text-lg font-semibold text-white">
          <span className="flex size-8 items-center justify-center rounded-full bg-white/15 backdrop-blur">
            <Home className="size-4" />
          </span>
          SoftStay
        </Link>
        <p className="absolute inset-x-8 bottom-10 text-xl font-medium leading-snug text-white">
          &ldquo;Booking my apartment took five minutes. Moving in felt like coming home.&rdquo;
        </p>
      </div>

      <div className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm space-y-8">
          <Link to="/" className="flex items-center gap-2 text-lg font-semibold md:hidden">
            <span className="flex size-8 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <Home className="size-4" />
            </span>
            SoftStay
          </Link>

          <div className="space-y-2">
            <h1 className="text-2xl font-semibold">{title}</h1>
            {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
          </div>

          {children}
        </div>
      </div>
    </div>
  )
}
