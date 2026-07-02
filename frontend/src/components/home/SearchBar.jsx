import { Building2, Euro, MapPin, Search, Users } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { PROPERTY_TYPES } from '@/lib/propertyType'

export function SearchBar() {
  const navigate = useNavigate()
  const [values, setValues] = useState({ city: '', price_max: '', property_type: '', rooms_min: '' })

  function handleChange(key, value) {
    setValues((prev) => ({ ...prev, [key]: value }))
  }

  function handleSearch() {
    const params = new URLSearchParams()
    Object.entries(values).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      }
    })
    navigate(`/listings?${params.toString()}`)
  }

  return (
    <div className="grid grid-cols-2 gap-4 rounded-3xl border border-border bg-card p-5 shadow-xl shadow-black/10 md:grid-cols-4 lg:grid-cols-[repeat(4,1fr)_auto] lg:gap-2">
      <div className="flex items-center gap-3 px-2">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <MapPin className="size-4" />
        </span>
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground">Location</p>
          <Input
            value={values.city}
            onChange={(event) => handleChange('city', event.target.value)}
            placeholder="Berlin"
            className="h-auto border-none p-0 text-sm font-semibold shadow-none focus-visible:ring-0"
          />
        </div>
      </div>

      <div className="flex items-center gap-3 px-2">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <Euro className="size-4" />
        </span>
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground">Max price</p>
          <Input
            type="number"
            min="0"
            value={values.price_max}
            onChange={(event) => handleChange('price_max', event.target.value)}
            placeholder="1500"
            className="h-auto border-none p-0 text-sm font-semibold shadow-none focus-visible:ring-0"
          />
        </div>
      </div>

      <div className="flex items-center gap-3 px-2">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <Building2 className="size-4" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-xs text-muted-foreground">Property type</p>
          <Select
            value={values.property_type}
            onChange={(event) => handleChange('property_type', event.target.value)}
            className="h-auto border-none p-0 pr-5 text-sm font-semibold shadow-none focus-visible:ring-0"
          >
            <option value="">Any type</option>
            {PROPERTY_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </Select>
        </div>
      </div>

      <div className="flex items-center gap-3 px-2">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <Users className="size-4" />
        </span>
        <div className="min-w-0">
          <p className="text-xs text-muted-foreground">Min rooms</p>
          <Input
            type="number"
            min="0"
            value={values.rooms_min}
            onChange={(event) => handleChange('rooms_min', event.target.value)}
            placeholder="1"
            className="h-auto border-none p-0 text-sm font-semibold shadow-none focus-visible:ring-0"
          />
        </div>
      </div>

      <Button size="lg" onClick={handleSearch} className="col-span-2 gap-2 rounded-2xl md:col-span-4 lg:col-span-1">
        <Search className="size-4" />
        Search
      </Button>
    </div>
  )
}
