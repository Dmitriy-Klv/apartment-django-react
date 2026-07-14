import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { createListing, getListing, updateListing } from '@/api/listings'
import { AuthProvider } from '@/context/AuthContext'
import { ListingFormPage } from '@/pages/ListingFormPage'

vi.mock('@/api/listings', () => ({
  createListing: vi.fn(),
  getListing: vi.fn(),
  updateListing: vi.fn(),
}))

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/listings/new']}>
        <AuthProvider>
          <ListingFormPage />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

async function fillRequiredFields(user) {
  await user.type(screen.getByLabelText('Title'), 'Nice apartment in Berlin')
  await user.type(screen.getByLabelText('Description'), 'Beautiful 2-room apartment in city center.')
  await user.type(screen.getByLabelText('City'), 'Berlin')
}

describe('ListingFormPage', () => {
  afterEach(() => {
    vi.clearAllMocks()
  })

  it('rejects a price of zero and does not submit', async () => {
    const user = userEvent.setup()
    renderPage()
    await fillRequiredFields(user)

    await user.type(screen.getByLabelText('Price per night (€)'), '0')
    await user.type(screen.getByLabelText('Rooms'), '2')
    await user.click(screen.getByRole('button', { name: /publish listing/i }))

    await waitFor(() => {
      expect(screen.getByText('Price must be greater than 0')).toBeInTheDocument()
    })
    expect(createListing).not.toHaveBeenCalled()
  })

  it('rejects a negative price and does not submit', async () => {
    const user = userEvent.setup()
    renderPage()
    await fillRequiredFields(user)

    await user.type(screen.getByLabelText('Price per night (€)'), '-100')
    await user.type(screen.getByLabelText('Rooms'), '2')
    await user.click(screen.getByRole('button', { name: /publish listing/i }))

    await waitFor(() => {
      expect(screen.getByText('Price must be greater than 0')).toBeInTheDocument()
    })
    expect(createListing).not.toHaveBeenCalled()
  })

  it('rejects a room count of zero and does not submit', async () => {
    const user = userEvent.setup()
    renderPage()
    await fillRequiredFields(user)

    await user.type(screen.getByLabelText('Price per night (€)'), '1200')
    await user.type(screen.getByLabelText('Rooms'), '0')
    await user.click(screen.getByRole('button', { name: /publish listing/i }))

    await waitFor(() => {
      expect(screen.getByText('Rooms must be at least 1')).toBeInTheDocument()
    })
    expect(createListing).not.toHaveBeenCalled()
  })

  it('submits when price and rooms are valid', async () => {
    const user = userEvent.setup()
    createListing.mockResolvedValue({ id: 1 })
    renderPage()
    await fillRequiredFields(user)

    await user.type(screen.getByLabelText('Price per night (€)'), '1200')
    await user.type(screen.getByLabelText('Rooms'), '2')
    await user.click(screen.getByRole('button', { name: /publish listing/i }))

    await waitFor(() => {
      expect(createListing).toHaveBeenCalledWith(
        expect.objectContaining({ price: 1200, rooms: 2 }),
      )
    })
  })

  it('surfaces a server-side price validation error on submit', async () => {
    const user = userEvent.setup()
    createListing.mockRejectedValue({
      response: { data: { price: ['Ensure this value is greater than or equal to 0.01.'] } },
    })
    renderPage()
    await fillRequiredFields(user)

    await user.type(screen.getByLabelText('Price per night (€)'), '1200')
    await user.type(screen.getByLabelText('Rooms'), '2')
    await user.click(screen.getByRole('button', { name: /publish listing/i }))

    await waitFor(() => {
      expect(screen.getByText('Ensure this value is greater than or equal to 0.01.')).toBeInTheDocument()
    })
  })
})
