export const BOOKING_STATUS = {
  pending: { label: 'Pending', className: 'bg-amber-100 text-amber-800' },
  confirmed: { label: 'Confirmed', className: 'bg-blue-100 text-blue-800' },
  rejected: { label: 'Rejected', className: 'bg-destructive/10 text-destructive' },
  canceled: { label: 'Canceled', className: 'bg-muted text-muted-foreground' },
  checked_in: { label: 'Checked in', className: 'bg-accent/10 text-accent' },
}

export function bookingStatusInfo(status) {
  return BOOKING_STATUS[status] || { label: status, className: 'bg-muted text-muted-foreground' }
}
