import { Home } from 'lucide-react'

import { cn } from '@/lib/utils'

export function ListingImage({ src, alt, className }) {
  if (src) {
    return <img src={src} alt={alt} className={cn('h-full w-full object-cover', className)} />
  }

  return (
    <div className={cn('flex h-full w-full items-center justify-center bg-muted text-muted-foreground', className)}>
      <Home className="size-6" />
    </div>
  )
}
