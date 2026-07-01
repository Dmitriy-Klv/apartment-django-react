import { Building2, Euro, MapPin, Search, Users } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const FIELDS = [
  { key: 'city', icon: MapPin, label: 'Location', placeholder: 'Berlin' },
  { key: 'price', icon: Euro, label: 'Price', placeholder: '500 - 1500' },
  { key: 'propertyType', icon: Building2, label: 'Property type', placeholder: 'Apartment' },
  { key: 'rooms', icon: Users, label: 'Rooms', placeholder: '1 - 2' },
]

export function SearchBar() {
  const navigate = useNavigate()
  const [values, setValues] = useState({ city: '', price: '', propertyType: '', rooms: '' })

  function handleChange(key, value) {
    setValues((prev) => ({ ...prev, [key]: value }))
  }

  function handleSearch() {
    const params = new URLSearchParams()
    if (values.city) params.set('city', values.city)
    navigate(`/listings?${params.toString()}`)
  }

  return (
    <div className="grid grid-cols-2 gap-4 rounded-3xl border border-border bg-card p-5 shadow-xl shadow-black/10 md:grid-cols-4 lg:grid-cols-[repeat(4,1fr)_auto] lg:gap-2">
      {FIELDS.map(({ key, icon: Icon, label, placeholder }) => (
        <div key={key} className="flex items-center gap-3 px-2">
          <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
            <Icon className="size-4" />
          </span>
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground">{label}</p>
            <Input
              value={values[key]}
              onChange={(event) => handleChange(key, event.target.value)}
              placeholder={placeholder}
              className="h-auto border-none p-0 text-sm font-semibold shadow-none focus-visible:ring-0"
            />
          </div>
        </div>
      ))}

      <Button size="lg" onClick={handleSearch} className="col-span-2 gap-2 rounded-2xl md:col-span-4 lg:col-span-1">
        <Search className="size-4" />
        Search
      </Button>
    </div>
  )
}
