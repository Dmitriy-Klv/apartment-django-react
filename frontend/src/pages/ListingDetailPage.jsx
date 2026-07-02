import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { BedDouble, Loader2, MapPin, Pencil, Star, ToggleLeft, ToggleRight, Trash2 } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { deleteListing, getListing, toggleListing } from '@/api/listings'
import { getListingReviews } from '@/api/reviews'
import { BookingForm } from '@/components/bookings/BookingForm'
import { PageLayout } from '@/components/layout/PageLayout'
import { ReviewList } from '@/components/reviews/ReviewList'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/context/AuthContext'
import { listingThumbnail } from '@/lib/images'
import { unwrapPage } from '@/lib/pagination'
import { propertyTypeLabel } from '@/lib/propertyType'

export function ListingDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuth()

  const { data: listing, isLoading } = useQuery({
    queryKey: ['listing', id],
    queryFn: () => getListing(id),
  })

  const { data: reviewsData } = useQuery({
    queryKey: ['listingReviews', id],
    queryFn: () => getListingReviews(id),
    enabled: Boolean(listing),
  })
  const reviews = unwrapPage(reviewsData).results

  const deleteMutation = useMutation({
    mutationFn: () => deleteListing(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myListings'] })
      navigate('/my-listings')
    },
  })

  const toggleMutation = useMutation({
    mutationFn: () => toggleListing(id),
    onSuccess: (updated) => {
      queryClient.setQueryData(['listing', id], updated)
      queryClient.invalidateQueries({ queryKey: ['myListings'] })
    },
  })

  if (isLoading) {
    return (
      <PageLayout>
        <Loader2 className="mx-auto size-6 animate-spin text-muted-foreground" />
      </PageLayout>
    )
  }

  if (!listing) {
    return (
      <PageLayout>
        <p className="text-center text-muted-foreground">Listing not found.</p>
      </PageLayout>
    )
  }

  const isOwner = user?.id === listing.owner
  const canBook = user?.role === 'tenant' && !isOwner

  return (
    <PageLayout>
      <div className="grid gap-10 lg:grid-cols-[1.6fr_1fr]">
        <div className="space-y-6">
          <div className="aspect-[16/9] overflow-hidden rounded-3xl">
            <img src={listingThumbnail(listing.id)} alt={listing.title} className="h-full w-full object-cover" />
          </div>

          <div className="space-y-2">
            <div className="flex items-start justify-between gap-4">
              <h1 className="text-2xl font-semibold">{listing.title}</h1>
              {!listing.is_active && (
                <span className="shrink-0 rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                  Inactive
                </span>
              )}
            </div>
            <p className="flex items-center gap-1 text-muted-foreground">
              <MapPin className="size-4" />
              {[listing.district, listing.city, listing.postal_code].filter(Boolean).join(', ')}
            </p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <BedDouble className="size-4" />
                {listing.rooms} room{listing.rooms === 1 ? '' : 's'}
              </span>
              <span>{propertyTypeLabel(listing.property_type)}</span>
              {Number(listing.reviews_count) > 0 && (
                <span className="flex items-center gap-1">
                  <Star className="size-4 fill-accent text-accent" />
                  {Number(listing.average_rating).toFixed(1)} ({listing.reviews_count} review
                  {listing.reviews_count === 1 ? '' : 's'})
                </span>
              )}
            </div>
          </div>

          <p className="whitespace-pre-line leading-relaxed text-foreground/90">{listing.description}</p>

          {isOwner && (
            <div className="flex flex-wrap gap-2 rounded-2xl border border-border p-4">
              <Button variant="outline" size="sm" className="gap-2" onClick={() => navigate(`/listings/${listing.id}/edit`)}>
                <Pencil className="size-3.5" />
                Edit
              </Button>
              <Button variant="outline" size="sm" className="gap-2" onClick={() => toggleMutation.mutate()}>
                {listing.is_active ? <ToggleRight className="size-3.5" /> : <ToggleLeft className="size-3.5" />}
                {listing.is_active ? 'Deactivate' : 'Activate'}
              </Button>
              <Button
                variant="destructive"
                size="sm"
                className="gap-2"
                onClick={() => {
                  if (window.confirm('Delete this listing? This cannot be undone.')) {
                    deleteMutation.mutate()
                  }
                }}
              >
                <Trash2 className="size-3.5" />
                Delete
              </Button>
            </div>
          )}

          <div className="space-y-4 border-t border-border pt-8">
            <h2 className="text-lg font-semibold">Reviews</h2>
            <ReviewList reviews={reviews} />
          </div>
        </div>

        <div className="lg:sticky lg:top-6 lg:self-start">
          <div className="space-y-4 rounded-3xl border border-border bg-card p-6">
            <p className="text-2xl font-semibold">
              €{listing.price}
              <span className="text-sm font-normal text-muted-foreground"> / night</span>
            </p>

            {canBook ? (
              <BookingForm listing={listing} />
            ) : !user ? (
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Sign in as a tenant to book this listing.</p>
                <Button asChild size="lg" className="w-full rounded-full">
                  <Link to="/login">Sign in</Link>
                </Button>
              </div>
            ) : isOwner ? (
              <p className="text-sm text-muted-foreground">This is your own listing.</p>
            ) : (
              <p className="text-sm text-muted-foreground">Only tenant accounts can book listings.</p>
            )}
          </div>
        </div>
      </div>
    </PageLayout>
  )
}
