export function unwrapPage(data) {
  if (Array.isArray(data)) {
    return { results: data, count: data.length, next: null, previous: null }
  }
  return {
    results: data?.results ?? [],
    count: data?.count ?? 0,
    next: data?.next ?? null,
    previous: data?.previous ?? null,
  }
}
