import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { getPopularListings } from '@/api/history'
import { ListingCard } from '@/components/listings/ListingCard'
import { unwrapPage } from '@/lib/pagination'

export function PopularListings() {
  const { data, isLoading } = useQuery({ queryKey: ['popularListings'], queryFn: () => getPopularListings() })
  const listings = unwrapPage(data).results.slice(0, 3)

  if (isLoading || listings.length === 0) {
    return null
  }

  return (
    <section className="space-y-6 pb-24">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Trending right now</h2>
        <Link to="/listings" className="text-sm font-medium underline underline-offset-4">
          View all
        </Link>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {listings.map((listing) => (
          <ListingCard key={listing.id} listing={listing} />
        ))}
      </div>
    </section>
  )
}
