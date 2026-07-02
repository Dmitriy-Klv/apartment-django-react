import { Star } from 'lucide-react'

import { cn } from '@/lib/utils'

export function RatingStars({ value = 0, onChange, size = 'sm' }) {
  const stars = [1, 2, 3, 4, 5]
  const sizeClass = size === 'lg' ? 'size-6' : 'size-4'

  return (
    <div className="flex items-center gap-0.5">
      {stars.map((star) => (
        <button
          key={star}
          type="button"
          disabled={!onChange}
          onClick={() => onChange?.(star)}
          className={cn(!onChange && 'cursor-default')}
          aria-label={`${star} star${star > 1 ? 's' : ''}`}
        >
          <Star
            className={cn(sizeClass, star <= value ? 'fill-accent text-accent' : 'fill-none text-muted-foreground')}
          />
        </button>
      ))}
    </div>
  )
}
