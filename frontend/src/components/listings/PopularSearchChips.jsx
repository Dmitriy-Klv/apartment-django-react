import { useQuery } from '@tanstack/react-query'

import { getPopularSearches } from '@/api/history'
import { Button } from '@/components/ui/button'
import { unwrapPage } from '@/lib/pagination'

const MAX_CHIPS = 6

export function PopularSearchChips({ onSelect }) {
  const { data, isLoading } = useQuery({ queryKey: ['popularSearches'], queryFn: () => getPopularSearches() })
  const keywords = unwrapPage(data).results.slice(0, MAX_CHIPS)

  if (isLoading || keywords.length === 0) {
    return null
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs text-muted-foreground">Popular:</span>
      {keywords.map(({ keyword }) => (
        <Button
          key={keyword}
          type="button"
          variant="outline"
          size="sm"
          className="rounded-full"
          onClick={() => onSelect(keyword)}
        >
          {keyword}
        </Button>
      ))}
    </div>
  )
}
