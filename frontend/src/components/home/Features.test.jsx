import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Features } from '@/components/home/Features'

describe('Features', () => {
  it('renders exactly three feature cards', () => {
    render(<Features />)
    expect(screen.getAllByRole('heading', { level: 3 })).toHaveLength(3)
  })

  it('does not make payment or pricing claims', () => {
    render(<Features />)
    expect(screen.queryByText(/transparent pricing/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/hidden fees/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/price you pay/i)).not.toBeInTheDocument()
  })

  it('describes the search history feature instead', () => {
    render(<Features />)
    expect(screen.getByText('Search history that remembers')).toBeInTheDocument()
  })
})
