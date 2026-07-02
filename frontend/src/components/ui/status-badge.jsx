import { bookingStatusInfo } from '@/lib/bookingStatus'
import { cn } from '@/lib/utils'

export function StatusBadge({ status, className }) {
  const { label, className: variantClassName } = bookingStatusInfo(status)

  return (
    <span
      className={cn('inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium', variantClassName, className)}
    >
      {label}
    </span>
  )
}
