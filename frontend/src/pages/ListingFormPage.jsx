import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, useParams } from 'react-router-dom'
import { z } from 'zod'

import { createListing, getListing, updateListing } from '@/api/listings'
import { PageLayout } from '@/components/layout/PageLayout'
import { ListingPhotoManager } from '@/components/listings/ListingPhotoManager'
import { Banner } from '@/components/ui/banner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { PROPERTY_TYPES } from '@/lib/propertyType'

const listingSchema = z.object({
  title: z.string().min(3, 'At least 3 characters').max(200),
  description: z.string().min(10, 'At least 10 characters'),
  city: z.string().min(1, 'City is required').max(100),
  district: z.string().max(100).optional(),
  postal_code: z.string().max(10).optional(),
  price: z.coerce.number().positive('Price must be greater than 0'),
  rooms: z.coerce.number().int().positive('Rooms must be at least 1'),
  property_type: z.enum(['apartment', 'house', 'studio', 'room', 'villa']),
})

export function ListingFormPage() {
  const { id } = useParams()
  const isEditing = Boolean(id)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [serverError, setServerError] = useState('')

  const { data: existingListing } = useQuery({
    queryKey: ['listing', id],
    queryFn: () => getListing(id),
    enabled: isEditing,
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(listingSchema),
    defaultValues: { property_type: 'apartment' },
  })

  useEffect(() => {
    if (existingListing) {
      reset({
        title: existingListing.title,
        description: existingListing.description,
        city: existingListing.city,
        district: existingListing.district,
        postal_code: existingListing.postal_code,
        price: existingListing.price,
        rooms: existingListing.rooms,
        property_type: existingListing.property_type,
      })
    }
  }, [existingListing, reset])

  const mutation = useMutation({
    mutationFn: (values) => (isEditing ? updateListing(id, values) : createListing(values)),
    onSuccess: (listing) => {
      queryClient.invalidateQueries({ queryKey: ['myListings'] })
      queryClient.invalidateQueries({ queryKey: ['listings'] })
      navigate(isEditing ? `/listings/${listing.id}` : `/listings/${listing.id}/edit`)
    },
    onError: (error) => {
      const data = error.response?.data
      const firstError = data && typeof data === 'object' ? Object.values(data)[0] : null
      setServerError((Array.isArray(firstError) ? firstError[0] : firstError) || 'Could not save listing.')
    },
  })

  function onSubmit(values) {
    setServerError('')
    mutation.mutate(values)
  }

  return (
    <PageLayout>
      <div className="mx-auto max-w-2xl space-y-6">
        <h1 className="text-2xl font-semibold">{isEditing ? 'Edit listing' : 'Create a new listing'}</h1>

        <div className="space-y-1.5">
          <Label>Photos</Label>
          {isEditing && existingListing ? (
            <ListingPhotoManager listingId={id} photos={existingListing.photos} />
          ) : (
            <p className="rounded-2xl border border-dashed border-border p-4 text-sm text-muted-foreground">
              Save the listing first, then you can add up to 5 photos and choose a cover photo.
            </p>
          )}
        </div>

        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
          <div className="space-y-1.5">
            <Label htmlFor="title">Title</Label>
            <Input id="title" {...register('title')} />
            {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="description">Description</Label>
            <Textarea id="description" rows={5} {...register('description')} />
            {errors.description && <p className="text-xs text-destructive">{errors.description.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="city">City</Label>
              <Input id="city" {...register('city')} />
              {errors.city && <p className="text-xs text-destructive">{errors.city.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="district">District</Label>
              <Input id="district" {...register('district')} />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="postal_code">Postal code</Label>
              <Input id="postal_code" {...register('postal_code')} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="property_type">Property type</Label>
              <Select id="property_type" {...register('property_type')}>
                {PROPERTY_TYPES.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="price">Price per night (€)</Label>
              <Input id="price" type="number" min="0.01" step="0.01" {...register('price')} />
              {errors.price && <p className="text-xs text-destructive">{errors.price.message}</p>}
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="rooms">Rooms</Label>
              <Input id="rooms" type="number" min="1" step="1" {...register('rooms')} />
              {errors.rooms && <p className="text-xs text-destructive">{errors.rooms.message}</p>}
            </div>
          </div>

          <Banner variant="error">{serverError}</Banner>

          <Button type="submit" size="lg" className="rounded-full" disabled={isSubmitting || mutation.isPending}>
            {mutation.isPending ? <Loader2 className="size-4 animate-spin" /> : isEditing ? 'Save changes' : 'Publish listing'}
          </Button>
        </form>
      </div>
    </PageLayout>
  )
}
