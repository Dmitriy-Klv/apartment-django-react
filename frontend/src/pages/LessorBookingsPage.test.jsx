import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { getLessorBookings } from '@/api/bookings'
import { AuthProvider } from '@/context/AuthContext'
import { LessorBookingsPage } from '@/pages/LessorBookingsPage'

vi.mock('@/api/bookings', () => ({
  getLessorBookings: vi.fn(),
  updateBookingStatus: vi.fn(),
}))

const BOOKING = {
  id: 1,
  listing: 5,
  listing_title: 'Sunny flat in Berlin',
  start_date: '2026-08-01',
  end_date: '2026-08-05',
  price_per_night: '120.00',
  total_price: '480.00',
  status: 'pending',
  tenant_email: 'tenant@example.com',
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AuthProvider>
          <LessorBookingsPage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('LessorBookingsPage', () => {
  it('shows the booking total and nightly price frozen at booking time', async () => {
    getLessorBookings.mockResolvedValue({ results: [BOOKING], count: 1, next: null, previous: null })
    renderPage()

    expect(await screen.findByText('Sunny flat in Berlin')).toBeInTheDocument()
    expect(screen.getByText('€480.00 total (€120.00/night)')).toBeInTheDocument()
  })
})
