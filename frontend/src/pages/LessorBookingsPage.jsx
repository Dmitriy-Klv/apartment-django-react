import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { getLessorBookings, updateBookingStatus } from '@/api/bookings'
import { PageLayout } from '@/components/layout/PageLayout'
import { Banner } from '@/components/ui/banner'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { StatusBadge } from '@/components/ui/status-badge'
import { Textarea } from '@/components/ui/textarea'
import { extractApiError } from '@/lib/apiError'
import { unwrapPage } from '@/lib/pagination'
import { REJECTION_REASONS, rejectionReasonLabel } from '@/lib/rejectionReason'

function RejectForm({ bookingId, onCancel, onConfirm, isPending }) {
  const [reason, setReason] = useState('')
  const [note, setNote] = useState('')
  const noteRequired = reason === 'other'
  const canConfirm = reason && (!noteRequired || note.trim())
  const reasonFieldId = `reject-reason-${bookingId}`
  const noteFieldId = `reject-note-${bookingId}`

  return (
    <div className="space-y-3 rounded-xl border border-border bg-muted/30 p-3">
      <div className="space-y-1.5">
        <Label htmlFor={reasonFieldId}>Rejection reason</Label>
        <Select id={reasonFieldId} value={reason} onChange={(event) => setReason(event.target.value)}>
          <option value="" disabled>
            Select a reason
          </option>
          {REJECTION_REASONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      </div>

      {noteRequired && (
        <div className="space-y-1.5">
          <Label htmlFor={noteFieldId}>Please specify</Label>
          <Textarea
            id={noteFieldId}
            value={note}
            onChange={(event) => setNote(event.target.value)}
            placeholder="Explain the reason for rejecting this booking"
          />
        </div>
      )}

      <div className="flex gap-2">
        <Button
          size="sm"
          variant="destructive"
          disabled={!canConfirm || isPending}
          onClick={() => onConfirm(reason, note)}
        >
          Confirm rejection
        </Button>
        <Button size="sm" variant="outline" disabled={isPending} onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </div>
  )
}

function LessorBookingRow({ booking }) {
  const queryClient = useQueryClient()
  const [error, setError] = useState('')
  const [isRejecting, setIsRejecting] = useState(false)

  const mutation = useMutation({
    mutationFn: ({ nextStatus, rejectionReason, rejectionNote }) =>
      updateBookingStatus(booking.id, nextStatus, { rejectionReason, rejectionNote }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lessorBookings'] })
      setIsRejecting(false)
    },
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

      {booking.status === 'rejected' && booking.rejection_reason && (
        <p className="text-sm text-muted-foreground">
          Reason: {rejectionReasonLabel(booking.rejection_reason)}
          {booking.rejection_note && ` — ${booking.rejection_note}`}
        </p>
      )}

      <Banner variant="error">{error}</Banner>

      {isRejecting ? (
        <RejectForm
          bookingId={booking.id}
          isPending={mutation.isPending}
          onCancel={() => setIsRejecting(false)}
          onConfirm={(reason, note) =>
            mutation.mutate({ nextStatus: 'rejected', rejectionReason: reason, rejectionNote: note })
          }
        />
      ) : (
        <div className="flex flex-wrap gap-2">
          {booking.status === 'pending' && (
            <>
              <Button size="sm" disabled={mutation.isPending} onClick={() => mutation.mutate({ nextStatus: 'confirmed' })}>
                Confirm
              </Button>
              <Button variant="outline" size="sm" disabled={mutation.isPending} onClick={() => setIsRejecting(true)}>
                Reject
              </Button>
            </>
          )}
          {booking.status === 'confirmed' && (
            <Button size="sm" disabled={mutation.isPending} onClick={() => mutation.mutate({ nextStatus: 'checked_in' })}>
              Mark as checked in
            </Button>
          )}
        </div>
      )}
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
