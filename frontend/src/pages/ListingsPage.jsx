import { useQuery } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { getListings } from '@/api/listings'
import { PageLayout } from '@/components/layout/PageLayout'
import { ListingCard } from '@/components/listings/ListingCard'
import { ListingFilters } from '@/components/listings/ListingFilters'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { unwrapPage } from '@/lib/pagination'

const FILTER_KEYS = ['search', 'city', 'district', 'price_min', 'price_max', 'rooms_min', 'rooms_max', 'property_type']

const EMPTY_FILTERS = Object.fromEntries(FILTER_KEYS.map((key) => [key, '']))

const ORDERING_OPTIONS = [
  { value: '-created_at', label: 'Newest first' },
  { value: 'created_at', label: 'Oldest first' },
  { value: 'price', label: 'Price: low to high' },
  { value: '-price', label: 'Price: high to low' },
  { value: '-views_count', label: 'Most viewed' },
  { value: '-average_rating', label: 'Top rated' },
]

function paramsToFilters(searchParams) {
  const filters = {}
  FILTER_KEYS.forEach((key) => {
    filters[key] = searchParams.get(key) || ''
  })
  return filters
}

export function ListingsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [draft, setDraft] = useState(() => paramsToFilters(searchParams))

  const page = Number(searchParams.get('page') || '1')
  const ordering = searchParams.get('ordering') || '-created_at'

  const queryParams = useMemo(() => {
    const params = { ordering, page }
    FILTER_KEYS.forEach((key) => {
      const value = searchParams.get(key)
      if (value) {
        params[key] = value
      }
    })
    return params
  }, [searchParams, ordering, page])

  const { data, isLoading, isError } = useQuery({
    queryKey: ['listings', queryParams],
    queryFn: () => getListings(queryParams),
    placeholderData: (previous) => previous,
  })

  const { results, count, next, previous } = unwrapPage(data)

  function updateParams(nextValues) {
    const params = new URLSearchParams(searchParams)
    Object.entries(nextValues).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      } else {
        params.delete(key)
      }
    })
    params.delete('page')
    setSearchParams(params)
  }

  function handleReset() {
    setDraft(EMPTY_FILTERS)
    setSearchParams({})
  }

  function handlePopularSearchSelect(keyword) {
    setDraft((prev) => ({ ...prev, search: keyword }))
    updateParams({ search: keyword })
  }

  function handleOrderingChange(event) {
    const params = new URLSearchParams(searchParams)
    params.set('ordering', event.target.value)
    params.delete('page')
    setSearchParams(params)
  }

  function goToPage(nextPage) {
    const params = new URLSearchParams(searchParams)
    params.set('page', nextPage)
    setSearchParams(params)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <PageLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold">Apartments for rent</h1>

        <ListingFilters
          values={draft}
          onChange={(key, value) => setDraft((prev) => ({ ...prev, [key]: value }))}
          onSubmit={() => updateParams(draft)}
          onReset={handleReset}
          onPopularSearchSelect={handlePopularSearchSelect}
        />

        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            {isLoading ? 'Loading…' : `${count} listing${count === 1 ? '' : 's'} found`}
          </p>
          <Select value={ordering} onChange={handleOrderingChange} className="w-auto">
            {ORDERING_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        </div>

        {isError && <p className="text-sm text-destructive">Could not load listings. Please try again.</p>}

        {isLoading ? (
          <Loader2 className="mx-auto size-6 animate-spin text-muted-foreground" />
        ) : results.length === 0 ? (
          <p className="py-16 text-center text-muted-foreground">No listings match your filters.</p>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {results.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}

        {(next || previous) && (
          <div className="flex items-center justify-center gap-4 pt-4">
            <Button variant="outline" disabled={!previous} onClick={() => goToPage(page - 1)}>
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">Page {page}</span>
            <Button variant="outline" disabled={!next} onClick={() => goToPage(page + 1)}>
              Next
            </Button>
          </div>
        )}
      </div>
    </PageLayout>
  )
}
