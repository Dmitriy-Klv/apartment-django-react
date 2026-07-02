import { BedDouble, MapPin, Star } from 'lucide-react'
import { Link } from 'react-router-dom'

import { ListingImage } from '@/components/listings/ListingImage'
import { propertyTypeLabel } from '@/lib/propertyType'

export function ListingCard({ listing }) {
  return (
    <Link
      to={`/listings/${listing.id}`}
      className="group block overflow-hidden rounded-3xl border border-border bg-card transition-shadow hover:shadow-lg hover:shadow-black/5"
    >
      <div className="aspect-[4/3] overflow-hidden">
        <ListingImage
          src={listing.cover_image}
          alt={listing.title}
          className="transition-transform duration-500 group-hover:scale-105"
        />
      </div>

      <div className="space-y-2 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="line-clamp-1 font-semibold">{listing.title}</h3>
          {Number(listing.reviews_count) > 0 && (
            <span className="flex shrink-0 items-center gap-1 text-sm text-muted-foreground">
              <Star className="size-3.5 fill-accent text-accent" />
              {Number(listing.average_rating).toFixed(1)}
            </span>
          )}
        </div>

        <p className="flex items-center gap-1 text-sm text-muted-foreground">
          <MapPin className="size-3.5" />
          {[listing.district, listing.city].filter(Boolean).join(', ')}
        </p>

        <div className="flex items-center justify-between pt-1">
          <p className="flex items-center gap-1 text-sm text-muted-foreground">
            <BedDouble className="size-3.5" />
            {listing.rooms} room{listing.rooms === 1 ? '' : 's'} · {propertyTypeLabel(listing.property_type)}
          </p>
          <p className="font-semibold">
            €{listing.price}
            <span className="text-sm font-normal text-muted-foreground"> /night</span>
          </p>
        </div>
      </div>
    </Link>
  )
}
