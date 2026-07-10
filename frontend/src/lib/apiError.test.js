import { describe, expect, it } from 'vitest'

import { extractApiError } from '@/lib/apiError'

const FALLBACK = 'Something went wrong.'

describe('extractApiError', () => {
  it('returns the fallback when the error has no response', () => {
    expect(extractApiError(new Error('network error'), FALLBACK)).toBe(FALLBACK)
  })

  it('reads a detail-shaped response body', () => {
    const error = { response: { data: { detail: 'Listing is already booked for the selected dates.' } } }
    expect(extractApiError(error, FALLBACK)).toBe('Listing is already booked for the selected dates.')
  })

  it('reads a non_field_errors-shaped response body', () => {
    const error = { response: { data: { non_field_errors: ['End date must be after start date.'] } } }
    expect(extractApiError(error, FALLBACK)).toBe('End date must be after start date.')
  })

  it('reads a field-specific error when no detail or non_field_errors is present', () => {
    const error = { response: { data: { start_date: ['Start date cannot be in the past.'] } } }
    expect(extractApiError(error, FALLBACK)).toBe('Start date cannot be in the past.')
  })

  it('reads a flat array response body', () => {
    const error = { response: { data: ['Listing is already booked for the selected dates.'] } }
    expect(extractApiError(error, FALLBACK)).toBe('Listing is already booked for the selected dates.')
  })

  it('falls back when the response body is an empty object', () => {
    const error = { response: { data: {} } }
    expect(extractApiError(error, FALLBACK)).toBe(FALLBACK)
  })
})
