import { Search, X } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { PROPERTY_TYPES } from '@/lib/propertyType'

export function ListingFilters({ values, onChange, onSubmit, onReset }) {
  function handleSubmit(event) {
    event.preventDefault()
    onSubmit()
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 rounded-3xl border border-border bg-card p-5 sm:grid-cols-2 lg:grid-cols-4">
      <div className="space-y-1.5 lg:col-span-2">
        <Label htmlFor="search">Keyword</Label>
        <Input
          id="search"
          placeholder="Title or description"
          value={values.search}
          onChange={(event) => onChange('search', event.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="city">City</Label>
        <Input id="city" placeholder="Berlin" value={values.city} onChange={(event) => onChange('city', event.target.value)} />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="district">District</Label>
        <Input
          id="district"
          placeholder="Mitte"
          value={values.district}
          onChange={(event) => onChange('district', event.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="price_min">Min price (€)</Label>
        <Input
          id="price_min"
          type="number"
          min="0"
          value={values.price_min}
          onChange={(event) => onChange('price_min', event.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="price_max">Max price (€)</Label>
        <Input
          id="price_max"
          type="number"
          min="0"
          value={values.price_max}
          onChange={(event) => onChange('price_max', event.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="rooms_min">Min rooms</Label>
        <Input
          id="rooms_min"
          type="number"
          min="0"
          value={values.rooms_min}
          onChange={(event) => onChange('rooms_min', event.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="rooms_max">Max rooms</Label>
        <Input
          id="rooms_max"
          type="number"
          min="0"
          value={values.rooms_max}
          onChange={(event) => onChange('rooms_max', event.target.value)}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="property_type">Property type</Label>
        <Select id="property_type" value={values.property_type} onChange={(event) => onChange('property_type', event.target.value)}>
          <option value="">Any type</option>
          {PROPERTY_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </Select>
      </div>

      <div className="flex items-end gap-2 lg:col-span-4">
        <Button type="submit" size="lg" className="gap-2 rounded-full">
          <Search className="size-4" />
          Apply filters
        </Button>
        <Button type="button" variant="ghost" size="lg" className="gap-2 rounded-full" onClick={onReset}>
          <X className="size-4" />
          Reset
        </Button>
      </div>
    </form>
  )
}
