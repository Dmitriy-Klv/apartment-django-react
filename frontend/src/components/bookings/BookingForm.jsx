import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { createBooking, getListingBookedDates } from '@/api/bookings'
import { Banner } from '@/components/ui/banner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { extractApiError } from '@/lib/apiError'

function nightsBetween(start, end) {
  if (!start || !end) {
    return 0
  }
  const diff = (new Date(end) - new Date(start)) / (1000 * 60 * 60 * 24)
  return diff > 0 ? diff : 0
}

const EMPTY_RANGES = []

function rangesOverlap(startDate, endDate, bookedRanges) {
  if (!startDate || !endDate) {
    return false
  }
  return bookedRanges.some((range) => startDate < range.end_date && endDate > range.start_date)
}

export function BookingForm({ listing }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const today = new Date().toISOString().split('T')[0]
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [error, setError] = useState('')

  const { data: bookedDates } = useQuery({
    queryKey: ['bookedDates', listing.id],
    queryFn: () => getListingBookedDates(listing.id),
  })
  const bookedRanges = bookedDates ?? EMPTY_RANGES

  const nights = nightsBetween(startDate, endDate)
  const estimatedTotal = nights * Number(listing.price)
  const hasOverlap = useMemo(() => rangesOverlap(startDate, endDate, bookedRanges), [startDate, endDate, bookedRanges])

  const mutation = useMutation({
    mutationFn: () => createBooking({ listing: listing.id, start_date: startDate, end_date: endDate }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myBookings'] })
      navigate('/my-bookings')
    },
    onError: (mutationError) => {
      setError(extractApiError(mutationError, 'Could not create booking. Please check the dates.'))
    },
  })

  function handleSubmit(event) {
    event.preventDefault()
    setError('')
    if (!startDate || !endDate) {
      setError('Please select both check-in and check-out dates.')
      return
    }
    if (hasOverlap) {
      setError('These dates overlap an existing booking. Please choose different dates.')
      return
    }
    mutation.mutate()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1.5">
          <Label htmlFor="start_date">Check-in</Label>
          <Input id="start_date" type="date" min={today} value={startDate} onChange={(event) => setStartDate(event.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="end_date">Check-out</Label>
          <Input
            id="end_date"
            type="date"
            min={startDate || today}
            value={endDate}
            onChange={(event) => setEndDate(event.target.value)}
          />
        </div>
      </div>

      {nights > 0 && (
        <p className="text-sm text-muted-foreground">
          {nights} night{nights === 1 ? '' : 's'} · estimated total €{estimatedTotal.toFixed(2)}
        </p>
      )}

      {hasOverlap && (
        <Banner variant="error">These dates overlap an existing booking. Please choose different dates.</Banner>
      )}
      <Banner variant="error">{error}</Banner>

      <Button type="submit" size="lg" className="w-full rounded-full" disabled={mutation.isPending || hasOverlap}>
        {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : 'Request to book'}
      </Button>
    </form>
  )
}
