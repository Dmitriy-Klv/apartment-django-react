import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { getListing } from '@/api/listings'
import { getListingReviews } from '@/api/reviews'
import { AuthProvider } from '@/context/AuthContext'
import { ListingDetailPage } from '@/pages/ListingDetailPage'

vi.mock('@/api/listings', () => ({
  getListing: vi.fn(),
  deleteListing: vi.fn(),
  toggleListing: vi.fn(),
}))

vi.mock('@/api/reviews', () => ({
  getListingReviews: vi.fn(),
}))

const LISTING = {
  id: 1,
  owner: 5,
  title: 'Sunny flat in Berlin',
  description: 'A lovely place.',
  city: 'Berlin',
  district: 'Mitte',
  postal_code: '10115',
  price: '900.00',
  rooms: 2,
  property_type: 'apartment',
  photos: [],
  cover_image: null,
  is_active: true,
  reviews_count: 0,
  average_rating: '0.00',
  views_count: 15,
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <ListingDetailPage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ListingDetailPage', () => {
  it('renders the view count', async () => {
    getListing.mockResolvedValue(LISTING)
    getListingReviews.mockResolvedValue({ results: [], count: 0, next: null, previous: null })
    renderPage()

    expect(await screen.findByText('15 views')).toBeInTheDocument()
  })

  it('uses the singular form for exactly one view', async () => {
    getListing.mockResolvedValue({ ...LISTING, views_count: 1 })
    getListingReviews.mockResolvedValue({ results: [], count: 0, next: null, previous: null })
    renderPage()

    expect(await screen.findByText('1 view')).toBeInTheDocument()
  })

  it('renders zero views without crashing', async () => {
    getListing.mockResolvedValue({ ...LISTING, views_count: 0 })
    getListingReviews.mockResolvedValue({ results: [], count: 0, next: null, previous: null })
    renderPage()

    expect(await screen.findByText('0 views')).toBeInTheDocument()
  })
})
