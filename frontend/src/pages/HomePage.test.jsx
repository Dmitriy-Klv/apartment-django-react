import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { getPopularListings } from '@/api/history'
import { AuthProvider } from '@/context/AuthContext'
import { HomePage } from '@/pages/HomePage'

vi.mock('@/api/history', () => ({
  getPopularListings: vi.fn(),
}))

const LISTING = {
  id: 1,
  title: 'Sunny flat',
  city: 'Berlin',
  district: 'Mitte',
  rooms: 2,
  price: '900.00',
  property_type: 'apartment',
  cover_image: null,
  reviews_count: 0,
  average_rating: '0.00',
}

function renderHomePage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <HomePage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('HomePage', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('shows trending listings above the feature highlights', async () => {
    getPopularListings.mockResolvedValue({ count: 1, next: null, previous: null, results: [LISTING] })
    renderHomePage()

    const trending = await screen.findByText('Trending right now')
    const features = screen.getByText('Verified listings')

    expect(trending.compareDocumentPosition(features) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })
})
