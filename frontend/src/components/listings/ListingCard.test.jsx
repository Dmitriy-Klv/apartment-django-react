import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { ListingCard } from '@/components/listings/ListingCard'

const LISTING = {
  id: 1,
  title: 'Sunny flat in Berlin',
  city: 'Berlin',
  district: 'Mitte',
  rooms: 2,
  price: '900.00',
  property_type: 'apartment',
  cover_image: null,
  reviews_count: 3,
  average_rating: '4.50',
  views_count: 42,
}

function renderCard(listing) {
  return render(
    <MemoryRouter>
      <ListingCard listing={listing} />
    </MemoryRouter>,
  )
}

describe('ListingCard', () => {
  it('renders the view count', () => {
    renderCard(LISTING)
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('renders the view count alongside the rating', () => {
    renderCard(LISTING)
    expect(screen.getByText('4.5')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('renders the view count even when there are no reviews yet', () => {
    renderCard({ ...LISTING, reviews_count: 0, views_count: 7 })
    expect(screen.getByText('7')).toBeInTheDocument()
    expect(screen.queryByText('4.5')).not.toBeInTheDocument()
  })

  it('renders zero views without crashing', () => {
    renderCard({ ...LISTING, views_count: 0 })
    expect(screen.getByText('0')).toBeInTheDocument()
  })
})
