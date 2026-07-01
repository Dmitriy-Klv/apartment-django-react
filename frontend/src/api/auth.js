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
