import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2, Pencil, Plus, ToggleLeft, ToggleRight, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'

import { deleteListing, getMyListings, toggleListing } from '@/api/listings'
import { PageLayout } from '@/components/layout/PageLayout'
import { ListingImage } from '@/components/listings/ListingImage'
import { Button } from '@/components/ui/button'
import { unwrapPage } from '@/lib/pagination'
import { propertyTypeLabel } from '@/lib/propertyType'

export function MyListingsPage() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({ queryKey: ['myListings'], queryFn: getMyListings })
  const listings = unwrapPage(data).results

  const toggleMutation = useMutation({
    mutationFn: (id) => toggleListing(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['myListings'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => deleteListing(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['myListings'] }),
  })

  return (
    <PageLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold">My listings</h1>
          <Button asChild size="lg" className="gap-2 rounded-full">
            <Link to="/listings/new">
              <Plus className="size-4" />
              New listing
            </Link>
          </Button>
        </div>

        {isLoading ? (
          <Loader2 className="mx-auto size-6 animate-spin text-muted-foreground" />
        ) : listings.length === 0 ? (
          <p className="py-16 text-center text-muted-foreground">You haven&apos;t published any listings yet.</p>
        ) : (
          <div className="space-y-3">
            {listings.map((listing) => (
              <div key={listing.id} className="flex items-center gap-4 rounded-2xl border border-border bg-card p-4">
                <div className="size-16 shrink-0 overflow-hidden rounded-xl">
                  <ListingImage src={listing.cover_image} alt={listing.title} />
                </div>

                <div className="min-w-0 flex-1">
                  <Link to={`/listings/${listing.id}`} className="font-semibold hover:underline">
                    {listing.title}
                  </Link>
                  <p className="text-sm text-muted-foreground">
                    {listing.city} · {propertyTypeLabel(listing.property_type)} · €{listing.price}/night
                  </p>
                </div>

                <span
                  className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${
                    listing.is_active ? 'bg-accent/10 text-accent' : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {listing.is_active ? 'Active' : 'Inactive'}
                </span>

                <div className="flex shrink-0 gap-1">
                  <Button variant="ghost" size="icon" asChild>
                    <Link to={`/listings/${listing.id}/edit`}>
                      <Pencil className="size-4" />
                    </Link>
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => toggleMutation.mutate(listing.id)}>
                    {listing.is_active ? <ToggleRight className="size-4" /> : <ToggleLeft className="size-4" />}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      if (window.confirm('Delete this listing? This cannot be undone.')) {
                        deleteMutation.mutate(listing.id)
                      }
                    }}
                  >
                    <Trash2 className="size-4 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </PageLayout>
  )
}
