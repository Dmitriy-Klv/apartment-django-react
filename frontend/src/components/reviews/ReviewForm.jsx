import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useState } from 'react'

import { createReview } from '@/api/reviews'
import { Banner } from '@/components/ui/banner'
import { Button } from '@/components/ui/button'
import { RatingStars } from '@/components/ui/rating-stars'
import { Textarea } from '@/components/ui/textarea'
import { extractApiError } from '@/lib/apiError'

export function ReviewForm({ booking, onDone }) {
  const queryClient = useQueryClient()
  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () => createReview({ booking: booking.id, rating, comment }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['listingReviews', String(booking.listing)] })
      onDone?.()
    },
    onError: (mutationError) => {
      setError(extractApiError(mutationError, 'Could not submit review.'))
    },
  })

  function handleSubmit(event) {
    event.preventDefault()
    setError('')
    if (!comment.trim()) {
      setError('Please add a short comment.')
      return
    }
    mutation.mutate()
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-2xl border border-border p-4">
      <RatingStars value={rating} onChange={setRating} size="lg" />
      <Textarea
        placeholder="How was your stay?"
        value={comment}
        onChange={(event) => setComment(event.target.value)}
      />
      <Banner variant="error">{error}</Banner>
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={mutation.isPending}>
          {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : 'Submit review'}
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={onDone}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
