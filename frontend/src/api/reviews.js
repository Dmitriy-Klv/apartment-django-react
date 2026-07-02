import { apiClient } from '@/api/client'

export async function getListingReviews(listingId, params = {}) {
  const response = await apiClient.get(`/listings/${listingId}/reviews/`, { params })
  return response.data
}

export async function createReview(data) {
  const response = await apiClient.post('/reviews/', data)
  return response.data
}
