import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { getMyBookings, updateBookingStatus } from '@/api/bookings'
import { getListingReviews } from '@/api/reviews'
import { PageLayout } from '@/components/layout/PageLayout'
import { ReviewForm } from '@/components/reviews/ReviewForm'
import { Banner } from '@/components/ui/banner'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/status-badge'
import { extractApiError } from '@/lib/apiError'
import { unwrapPage } from '@/lib/pagination'
import { rejectionReasonLabel } from '@/lib/rejectionReason'

function BookingRow({ booking }) {
  const queryClient = useQueryClient()
  const [showReviewForm, setShowReviewForm] = useState(false)
  const [error, setError] = useState('')

  const { data: reviewsData } = useQuery({
    queryKey: ['listingReviews', String(booking.listing)],
    queryFn: () => getListingReviews(booking.listing),
    enabled: booking.status === 'checked_in',
  })
  const alreadyReviewed = unwrapPage(reviewsData).results.some((review) => review.booking === booking.id)

  const cancelMutation = useMutation({
    mutationFn: () => updateBookingStatus(booking.id, 'canceled'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['myBookings'] }),
    onError: (mutationError) => {
      setError(extractApiError(mutationError, 'Could not cancel booking.'))
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
        </div>
        <StatusBadge status={booking.status} />
      </div>

      {booking.status === 'rejected' && booking.rejection_reason && (
        <p className="text-sm text-muted-foreground">
          Reason: {rejectionReasonLabel(booking.rejection_reason)}
          {booking.rejection_note && ` — ${booking.rejection_note}`}
        </p>
      )}

      <Banner variant="error">{error}</Banner>

      <div className="flex flex-wrap items-center gap-2">
        {booking.status === 'pending' && (
          <Button variant="outline" size="sm" disabled={cancelMutation.isPending} onClick={() => cancelMutation.mutate()}>
            Cancel booking
          </Button>
        )}
        {booking.status === 'checked_in' && !alreadyReviewed && !showReviewForm && (
          <Button variant="outline" size="sm" onClick={() => setShowReviewForm(true)}>
            Leave a review
          </Button>
        )}
        {booking.status === 'checked_in' && alreadyReviewed && (
          <p className="text-sm text-muted-foreground">You already reviewed this stay.</p>
        )}
      </div>

      {showReviewForm && <ReviewForm booking={booking} onDone={() => setShowReviewForm(false)} />}
    </div>
  )
}

export function MyBookingsPage() {
  const { data, isLoading } = useQuery({ queryKey: ['myBookings'], queryFn: getMyBookings })
  const bookings = unwrapPage(data).results

  return (
    <PageLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">My bookings</h1>

        {isLoading ? (
          <Loader2 className="mx-auto size-6 animate-spin text-muted-foreground" />
        ) : bookings.length === 0 ? (
          <p className="py-16 text-center text-muted-foreground">
            No bookings yet.{' '}
            <Link to="/listings" className="underline underline-offset-4">
              Browse listings
            </Link>
            .
          </p>
        ) : (
          <div className="space-y-3">
            {bookings.map((booking) => (
              <BookingRow key={booking.id} booking={booking} />
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  )
}
