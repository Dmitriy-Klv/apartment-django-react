import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { getLessorBookings, updateBookingStatus } from '@/api/bookings'
import { PageLayout } from '@/components/layout/PageLayout'
import { Banner } from '@/components/ui/banner'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/status-badge'
import { extractApiError } from '@/lib/apiError'
import { unwrapPage } from '@/lib/pagination'

function LessorBookingRow({ booking }) {
  const queryClient = useQueryClient()
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: (status) => updateBookingStatus(booking.id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lessorBookings'] }),
    onError: (mutationError) => {
      setError(extractApiError(mutationError, 'Could not update booking.'))
    },
  })

  return (
    <div className="space-y-3 rounded-2xl border border-border bg-card p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link to={`/listings/${booking.listing}`} className="font-semibold hover:underline">
            {booking.listing_title}
          </Link>
          <p className="text-sm text-muted-foreground">
            {booking.start_date} → {booking.end_date}
          </p>
          <p className="text-sm text-muted-foreground">
            €{booking.total_price} total (€{booking.price_per_night}/night)
          </p>
          <p className="text-xs text-muted-foreground">Guest: {booking.tenant_email}</p>
        </div>
        <StatusBadge status={booking.status} />
      </div>

      <Banner variant="error">{error}</Banner>

      <div className="flex flex-wrap gap-2">
        {booking.status === 'pending' && (
          <>
            <Button size="sm" disabled={mutation.isPending} onClick={() => mutation.mutate('confirmed')}>
              Confirm
            </Button>
            <Button variant="outline" size="sm" disabled={mutation.isPending} onClick={() => mutation.mutate('rejected')}>
              Reject
            </Button>
          </>
        )}
        {booking.status === 'confirmed' && (
          <Button size="sm" disabled={mutation.isPending} onClick={() => mutation.mutate('checked_in')}>
            Mark as checked in
          </Button>
        )}
      </div>
    </div>
  )
}

export function LessorBookingsPage() {
  const { data, isLoading } = useQuery({ queryKey: ['lessorBookings'], queryFn: getLessorBookings })
  const bookings = unwrapPage(data).results

  return (
    <PageLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">Bookings on my listings</h1>

        {isLoading ? (
          <Loader2 className="mx-auto size-6 animate-spin text-muted-foreground" />
        ) : bookings.length === 0 ? (
          <p className="py-16 text-center text-muted-foreground">No bookings yet.</p>
        ) : (
          <div className="space-y-3">
            {bookings.map((booking) => (
              <LessorBookingRow key={booking.id} booking={booking} />
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  )
}
