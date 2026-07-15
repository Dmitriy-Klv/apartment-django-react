import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ReviewList } from '@/components/reviews/ReviewList'

const REVIEW = {
  id: 1,
  rating: 4,
  comment: 'Great stay, would book again.',
  author_username: 'jane_lessor',
  created_at: '2026-07-15T10:00:00Z',
}

describe('ReviewList', () => {
  it('renders the author username above the comment', () => {
    render(<ReviewList reviews={[REVIEW]} />)
    expect(screen.getByText('jane_lessor')).toBeInTheDocument()
  })

  it('renders the comment text', () => {
    render(<ReviewList reviews={[REVIEW]} />)
    expect(screen.getByText('Great stay, would book again.')).toBeInTheDocument()
  })

  it('does not render an email address anywhere', () => {
    render(<ReviewList reviews={[REVIEW]} />)
    expect(screen.queryByText(/@/)).not.toBeInTheDocument()
  })

  it('shows a fallback message when there are no reviews', () => {
    render(<ReviewList reviews={[]} />)
    expect(screen.getByText('No reviews yet.')).toBeInTheDocument()
  })
})
