import axios from 'axios'

import { clearSession, getAccessToken, getRefreshToken, saveTokens } from '@/lib/authStorage'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const SKIP_REFRESH_PATHS = ['/auth/login/', '/auth/register/', '/auth/token/refresh/']

export const apiClient = axios.create({ baseURL })

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshPromise = null

async function refreshAccessToken() {
  const refresh = getRefreshToken()
  if (!refresh) {
    throw new Error('No refresh token available')
  }
  const response = await axios.post(`${baseURL}/auth/token/refresh/`, { refresh })
  saveTokens(response.data)
  return response.data.access
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error
    const isAuthEndpoint = SKIP_REFRESH_PATHS.some((path) => config?.url?.includes(path))

    if (response?.status !== 401 || config._retry || isAuthEndpoint) {
      return Promise.reject(error)
    }

    config._retry = true
    try {
      refreshPromise = refreshPromise || refreshAccessToken()
      const access = await refreshPromise
      refreshPromise = null
      config.headers.Authorization = `Bearer ${access}`
      return apiClient(config)
    } catch (refreshError) {
      refreshPromise = null
      clearSession()
      window.location.assign('/login')
      return Promise.reject(refreshError)
    }
  },
)
