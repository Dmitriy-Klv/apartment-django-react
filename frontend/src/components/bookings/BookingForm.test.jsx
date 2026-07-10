import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { getListingBookedDates } from '@/api/bookings'
import { BookingForm } from '@/components/bookings/BookingForm'

vi.mock('@/api/bookings', () => ({
  createBooking: vi.fn(),
  getListingBookedDates: vi.fn(),
}))

const LISTING = { id: 1, price: '100.00' }
const TODAY = new Date()

function daysFromNow(days) {
  const date = new Date(TODAY)
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

function renderForm() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <BookingForm listing={LISTING} />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('BookingForm', () => {
  beforeEach(() => {
    getListingBookedDates.mockResolvedValue([{ start_date: daysFromNow(10), end_date: daysFromNow(15) }])
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('warns and disables submit when the selected dates overlap an existing booking', async () => {
    const user = userEvent.setup()
    renderForm()

    await user.type(screen.getByLabelText('Check-in'), daysFromNow(12))
    await user.type(screen.getByLabelText('Check-out'), daysFromNow(14))

    await waitFor(() => {
      expect(screen.getByText(/overlap an existing booking/i)).toBeInTheDocument()
    })
    expect(screen.getByRole('button', { name: /request to book/i })).toBeDisabled()
  })

  it('allows submit when the selected dates are free', async () => {
    const user = userEvent.setup()
    renderForm()

    await user.type(screen.getByLabelText('Check-in'), daysFromNow(1))
    await user.type(screen.getByLabelText('Check-out'), daysFromNow(3))

    await waitFor(() => {
      expect(getListingBookedDates).toHaveBeenCalledWith(LISTING.id)
    })
    expect(screen.queryByText(/overlap an existing booking/i)).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /request to book/i })).not.toBeDisabled()
  })
})
