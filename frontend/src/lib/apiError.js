export function extractApiError(error, fallback) {
  const data = error?.response?.data
  if (!data) {
    return fallback
  }
  if (typeof data === 'string') {
    return data
  }
  if (Array.isArray(data)) {
    return data[0] ?? fallback
  }
  if (data.detail) {
    return data.detail
  }
  if (data.non_field_errors?.[0]) {
    return data.non_field_errors[0]
  }
  const firstFieldError = Object.values(data).find((value) => Array.isArray(value) && value.length > 0)
  return firstFieldError?.[0] ?? fallback
}
