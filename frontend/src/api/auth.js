import { apiClient } from '@/api/client'

export async function registerUser({ email, password, firstName, lastName, role }) {
  const response = await apiClient.post('/auth/register/', {
    email,
    password,
    first_name: firstName,
    last_name: lastName,
    role,
  })
  return response.data
}

export async function loginUser({ email, password }) {
  const response = await apiClient.post('/auth/login/', { email, password })
  return response.data
}

export async function getMe() {
  const response = await apiClient.get('/auth/me/')
  return response.data
}

export async function logoutUser(refresh) {
  await apiClient.post('/auth/logout/', { refresh })
}
