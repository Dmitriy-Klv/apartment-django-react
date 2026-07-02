export const PROPERTY_TYPES = [
  { value: 'apartment', label: 'Apartment' },
  { value: 'house', label: 'House' },
  { value: 'studio', label: 'Studio' },
  { value: 'room', label: 'Room' },
  { value: 'villa', label: 'Villa' },
]

export function propertyTypeLabel(value) {
  return PROPERTY_TYPES.find((type) => type.value === value)?.label || value
}
