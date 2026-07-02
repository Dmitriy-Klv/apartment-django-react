import { apiClient } from '@/api/client'

export async function getMyBookings(params = {}) {
  const response = await apiClient.get('/bookings/', { params })
  return response.data
}

export async function getLessorBookings(params = {}) {
  const response = await apiClient.get('/bookings/lessor/', { params })
  return response.data
}

export async function getBooking(id) {
  const response = await apiClient.get(`/bookings/${id}/`)
  return response.data
}

export async function createBooking(data) {
  const response = await apiClient.post('/bookings/', data)
  return response.data
}

export async function updateBookingStatus(id, status) {
  const response = await apiClient.patch(`/bookings/${id}/status/`, { status })
  return response.data
}
