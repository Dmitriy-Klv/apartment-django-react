import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { getPopularSearches } from '@/api/history'
import { getListings } from '@/api/listings'
import { AuthProvider } from '@/context/AuthContext'
import { ListingsPage } from '@/pages/ListingsPage'

vi.mock('@/api/listings', () => ({
  getListings: vi.fn(),
}))

vi.mock('@/api/history', () => ({
  getPopularSearches: vi.fn(),
}))

const LISTING = {
  id: 1,
  title: 'Sunny flat in Berlin',
  city: 'Berlin',
  district: 'Mitte',
  rooms: 2,
  price: '900.00',
  property_type: 'apartment',
  cover_image: null,
  reviews_count: 0,
  average_rating: '0.00',
  views_count: 0,
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/listings']}>
        <AuthProvider>
          <ListingsPage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ListingsPage', () => {
  it('runs a search for the clicked popular keyword without submitting the filters form', async () => {
    getListings.mockResolvedValue({ results: [LISTING], count: 1, next: null, previous: null })
    getPopularSearches.mockResolvedValue({
      results: [{ keyword: 'Berlin', total_count: 12 }],
      count: 1,
      next: null,
      previous: null,
    })
    const user = userEvent.setup()
    renderPage()

    await screen.findByText('Sunny flat in Berlin')
    getListings.mockClear()

    const chip = await screen.findByRole('button', { name: 'Berlin' })
    await user.click(chip)

    await vi.waitFor(() => {
      expect(getListings).toHaveBeenCalledWith(expect.objectContaining({ search: 'Berlin' }))
    })
    expect(screen.getByLabelText('Keyword')).toHaveValue('Berlin')
  })
})
