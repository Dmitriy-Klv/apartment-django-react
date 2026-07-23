import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'

import { getLessorBookings, updateBookingStatus } from '@/api/bookings'
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

  it('requires a rejection reason before confirming a reject', async () => {
    const user = userEvent.setup()
    getLessorBookings.mockResolvedValue({ results: [BOOKING], count: 1, next: null, previous: null })
    renderPage()

    await user.click(await screen.findByRole('button', { name: 'Reject' }))
    const confirmButton = screen.getByRole('button', { name: 'Confirm rejection' })
    expect(confirmButton).toBeDisabled()

    await user.selectOptions(screen.getByLabelText('Rejection reason'), 'dates_unavailable')
    expect(confirmButton).toBeEnabled()

    await user.click(confirmButton)
    expect(updateBookingStatus).toHaveBeenCalledWith(1, 'rejected', {
      rejectionReason: 'dates_unavailable',
      rejectionNote: '',
    })
  })

  it('requires a note when the rejection reason is "Other"', async () => {
    const user = userEvent.setup()
    getLessorBookings.mockResolvedValue({ results: [BOOKING], count: 1, next: null, previous: null })
    renderPage()

    await user.click(await screen.findByRole('button', { name: 'Reject' }))
    await user.selectOptions(screen.getByLabelText('Rejection reason'), 'other')
    const confirmButton = screen.getByRole('button', { name: 'Confirm rejection' })
    expect(confirmButton).toBeDisabled()

    await user.type(screen.getByLabelText('Please specify'), 'Owner needs the place that week.')
    expect(confirmButton).toBeEnabled()

    await user.click(confirmButton)
    expect(updateBookingStatus).toHaveBeenCalledWith(1, 'rejected', {
      rejectionReason: 'other',
      rejectionNote: 'Owner needs the place that week.',
    })
  })

  it('shows the rejection reason and note for an already rejected booking', async () => {
    const rejectedBooking = {
      ...BOOKING,
      status: 'rejected',
      rejection_reason: 'listing_unavailable',
      rejection_note: 'Under renovation until next month.',
    }
    getLessorBookings.mockResolvedValue({ results: [rejectedBooking], count: 1, next: null, previous: null })
    renderPage()

    expect(await screen.findByText('Reason: Listing temporarily unavailable — Under renovation until next month.')).toBeInTheDocument()
  })
})
