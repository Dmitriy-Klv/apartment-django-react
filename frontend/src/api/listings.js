import { apiClient } from '@/api/client'

export async function getListings(params = {}) {
  const response = await apiClient.get('/listings/', { params })
  return response.data
}

export async function getListing(id) {
  const response = await apiClient.get(`/listings/${id}/`)
  return response.data
}

export async function getMyListings() {
  const response = await apiClient.get('/listings/my/')
  return response.data
}

export async function createListing(data) {
  const response = await apiClient.post('/listings/', data)
  return response.data
}

export async function updateListing(id, data) {
  const response = await apiClient.patch(`/listings/${id}/`, data)
  return response.data
}

export async function deleteListing(id) {
  await apiClient.delete(`/listings/${id}/`)
}

export async function toggleListing(id) {
  const response = await apiClient.patch(`/listings/${id}/toggle/`)
  return response.data
}
