import { AlertCircle, CheckCircle2 } from 'lucide-react'

import { cn } from '@/lib/utils'

const VARIANTS = {
  success: 'bg-accent/10 text-accent',
  error: 'bg-destructive/10 text-destructive',
}

const ICONS = {
  success: CheckCircle2,
  error: AlertCircle,
}

export function Banner({ variant = 'error', children, className }) {
  if (!children) {
    return null
  }
  const Icon = ICONS[variant]

  return (
    <div className={cn('flex items-center gap-2 rounded-xl px-4 py-3 text-sm', VARIANTS[variant], className)}>
      <Icon className="size-4 shrink-0" />
      <span>{children}</span>
    </div>
  )
}
