import { RatingStars } from '@/components/ui/rating-stars'

export function ReviewList({ reviews }) {
  if (!reviews || reviews.length === 0) {
    return <p className="text-sm text-muted-foreground">No reviews yet.</p>
  }

  return (
    <div className="space-y-5">
      {reviews.map((review) => (
        <div key={review.id} className="space-y-1 border-b border-border pb-5 last:border-0">
          <div className="flex items-center justify-between">
            <RatingStars value={review.rating} />
            <span className="text-xs text-muted-foreground">
              {new Date(review.created_at).toLocaleDateString('en-GB')}
            </span>
          </div>
          <p className="text-sm font-medium">{review.author_username}</p>
          <p className="text-sm leading-relaxed">{review.comment}</p>
        </div>
      ))}
    </div>
  )
}
