import { apiClient } from '@/api/client'

export async function getPopularListings(params = {}) {
  const response = await apiClient.get('/history/listings/popular/', { params })
  return response.data
}

export async function getPopularSearches(params = {}) {
  const response = await apiClient.get('/history/searches/popular/', { params })
  return response.data
}
