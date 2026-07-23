export const REJECTION_REASONS = [
  { value: 'dates_unavailable', label: 'Dates no longer available' },
  { value: 'listing_unavailable', label: 'Listing temporarily unavailable' },
  { value: 'tenant_requirements_not_met', label: "Tenant doesn't meet requirements" },
  { value: 'suspicious_request', label: 'Suspicious or invalid request' },
  { value: 'other', label: 'Other' },
]

export function rejectionReasonLabel(value) {
  return REJECTION_REASONS.find((reason) => reason.value === value)?.label || value
}
