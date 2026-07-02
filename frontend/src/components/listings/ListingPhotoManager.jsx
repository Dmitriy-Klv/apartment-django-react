import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Image as ImageIcon, Loader2, Star, Trash2 } from 'lucide-react'
import { useState } from 'react'

import { deleteListingPhoto, setPrimaryPhoto, uploadListingPhoto } from '@/api/listings'
import { Banner } from '@/components/ui/banner'
import { cn } from '@/lib/utils'

const MAX_PHOTOS = 5
const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp']

export function ListingPhotoManager({ listingId, photos }) {
  const queryClient = useQueryClient()
  const [error, setError] = useState('')

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ['listing', String(listingId)] })
    queryClient.invalidateQueries({ queryKey: ['myListings'] })
    queryClient.invalidateQueries({ queryKey: ['listings'] })
  }

  const uploadMutation = useMutation({
    mutationFn: (file) => uploadListingPhoto(listingId, file),
    onSuccess: invalidate,
    onError: (mutationError) => {
      setError(mutationError.response?.data?.image?.[0] || 'Could not upload photo.')
    },
  })

  const setCoverMutation = useMutation({
    mutationFn: (photoId) => setPrimaryPhoto(listingId, photoId),
    onSuccess: invalidate,
  })

  const deleteMutation = useMutation({
    mutationFn: (photoId) => deleteListingPhoto(listingId, photoId),
    onSuccess: invalidate,
  })

  function handleFileChange(event) {
    const file = event.target.files?.[0]
    event.target.value = ''
    setError('')
    if (!file) {
      return
    }
    if (file.size > MAX_IMAGE_SIZE_BYTES) {
      setError('Image must be smaller than 5 MB.')
      return
    }
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      setError('Image must be JPEG, PNG, or WebP.')
      return
    }
    uploadMutation.mutate(file)
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-5 gap-3">
        {photos.map((photo) => (
          <div
            key={photo.id}
            data-photo-id={photo.id}
            className="group relative aspect-square overflow-hidden rounded-xl border border-border"
          >
            <img src={photo.image} alt="Listing" className="h-full w-full object-cover" />

            <div className="absolute inset-0 flex items-center justify-center gap-1.5 bg-black/50 opacity-0 transition-opacity group-hover:opacity-100">
              <button
                type="button"
                title="Set as cover photo"
                onClick={() => setCoverMutation.mutate(photo.id)}
                className="flex size-7 items-center justify-center rounded-full bg-white/90"
              >
                <Star className={cn('size-3.5', photo.is_primary ? 'fill-accent text-accent' : 'text-foreground')} />
              </button>
              <button
                type="button"
                title="Delete photo"
                onClick={() => deleteMutation.mutate(photo.id)}
                className="flex size-7 items-center justify-center rounded-full bg-white/90 text-destructive"
              >
                <Trash2 className="size-3.5" />
              </button>
            </div>

            {photo.is_primary && (
              <span className="absolute left-1 top-1 rounded-full bg-accent px-1.5 py-0.5 text-[10px] font-medium text-accent-foreground">
                Cover
              </span>
            )}
          </div>
        ))}

        {photos.length < MAX_PHOTOS && (
          <label className="flex aspect-square cursor-pointer flex-col items-center justify-center gap-1 rounded-xl border border-dashed border-border text-muted-foreground hover:border-foreground/30">
            {uploadMutation.isPending ? (
              <Loader2 className="size-5 animate-spin" />
            ) : (
              <ImageIcon className="size-5" />
            )}
            <span className="text-[11px]">Add photo</span>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={handleFileChange}
              disabled={uploadMutation.isPending}
            />
          </label>
        )}
      </div>

      <Banner variant="error">{error}</Banner>

      <p className="text-xs text-muted-foreground">
        Up to {MAX_PHOTOS} photos, JPEG/PNG/WebP, 5 MB each. Hover a photo and click the star to choose the cover
        photo shown on listing cards.
      </p>
    </div>
  )
}
