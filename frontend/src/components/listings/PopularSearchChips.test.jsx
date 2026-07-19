import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { getPopularSearches } from '@/api/history'
import { PopularSearchChips } from '@/components/listings/PopularSearchChips'

vi.mock('@/api/history', () => ({
  getPopularSearches: vi.fn(),
}))

function renderChips(onSelect = vi.fn()) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <PopularSearchChips onSelect={onSelect} />
    </QueryClientProvider>,
  )
}

describe('PopularSearchChips', () => {
  it('renders a chip for each popular keyword', async () => {
    getPopularSearches.mockResolvedValue({
      results: [
        { keyword: 'Berlin', total_count: 12 },
        { keyword: 'Munich', total_count: 8 },
      ],
      count: 2,
      next: null,
      previous: null,
    })
    renderChips()

    expect(await screen.findByRole('button', { name: 'Berlin' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Munich' })).toBeInTheDocument()
  })

  it('renders nothing when there are no popular keywords', async () => {
    getPopularSearches.mockResolvedValue({ results: [], count: 0, next: null, previous: null })
    const { container } = renderChips()

    await vi.waitFor(() => expect(getPopularSearches).toHaveBeenCalled())
    expect(container).toBeEmptyDOMElement()
  })

  it('calls onSelect with the clicked keyword', async () => {
    getPopularSearches.mockResolvedValue({
      results: [{ keyword: 'Berlin', total_count: 12 }],
      count: 1,
      next: null,
      previous: null,
    })
    const onSelect = vi.fn()
    const user = userEvent.setup()
    renderChips(onSelect)

    const chip = await screen.findByRole('button', { name: 'Berlin' })
    await user.click(chip)

    expect(onSelect).toHaveBeenCalledWith('Berlin')
  })

  it('renders chips as type="button" so they never submit a surrounding form', async () => {
    getPopularSearches.mockResolvedValue({
      results: [{ keyword: 'Berlin', total_count: 12 }],
      count: 1,
      next: null,
      previous: null,
    })
    renderChips()

    const chip = await screen.findByRole('button', { name: 'Berlin' })
    expect(chip).toHaveAttribute('type', 'button')
  })
})
