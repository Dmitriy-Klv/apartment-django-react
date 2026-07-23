import random
import uuid
from datetime import date, timedelta
from pathlib import Path

import environ
from django.core.files import File
from django.core.management.base import BaseCommand
from faker import Faker

from apps.bookings.models import Booking, BookingStatus, RejectionReason
from apps.history.services.search_history import SearchHistoryService
from apps.history.services.view_history import ViewHistoryService
from apps.listings.models import Listing, ListingPhoto, PropertyType
from apps.reviews.models import Review
from apps.users.models import User, UserRole
from apps.users.services.user import UserService

env = environ.Env()

SEED_EMAIL_DOMAIN = 'seed.example'
DEMO_PHOTO_DIR = Path(__file__).resolve().parent / 'demo_photo'
DEMO_PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

GERMAN_DISTRICTS = {
    'Berlin': ['Mitte', 'Kreuzberg', 'Charlottenburg', 'Prenzlauer Berg', 'Neukoelln'],
    'Munich': ['Schwabing', 'Maxvorstadt', 'Bogenhausen', 'Sendling'],
    'Hamburg': ['Altona', 'Eimsbuettel', 'St. Pauli', 'Winterhude'],
    'Cologne': ['Ehrenfeld', 'Deutz', 'Nippes', 'Lindenthal'],
    'Frankfurt': ['Sachsenhausen', 'Bornheim', 'Westend'],
}

LISTING_TITLES = [
    'Bright apartment near the park',
    'Cozy studio in the city center',
    'Spacious family house with garden',
    'Modern loft with great transport links',
    'Quiet room close to the university',
    'Renovated flat with a balcony',
    'Charming villa with private parking',
    'Sunny apartment with high ceilings',
]

SEARCH_KEYWORDS = [
    'Berlin apartment', 'cheap studio', 'furnished flat', 'pet friendly',
    'house with garden', 'Munich rent', 'Hamburg apartment', 'city center',
    'quiet neighborhood', 'student room',
]


class Command(BaseCommand):
    help = 'Seed the database with fake demo data (users, listings, bookings, reviews, history).'

    def add_arguments(self, parser):
        """Register the CLI options for this command."""
        parser.add_argument('--lessors', type=int, default=6, help='Number of random lessor accounts to create.')
        parser.add_argument('--tenants', type=int, default=10, help='Number of random tenant accounts to create.')
        parser.add_argument('--listings', type=int, default=24, help='Number of listings to create.')
        parser.add_argument('--clear', action='store_true', help='Delete previously seeded data before reseeding.')

    def handle(self, *args, **options):
        """Clear previous seed data if requested, then seed users, listings, bookings, reviews and history."""
        self.fake = Faker()
        self.fake_de = Faker('de_DE')

        if options['clear']:
            self._clear_seed_data()

        demo_photos = self._discover_demo_photos()
        if not demo_photos:
            self.stdout.write(self.style.WARNING(
                f'No demo photos found in {DEMO_PHOTO_DIR} — listings will be seeded without photos.'
            ))

        lessors = self._create_users(options['lessors'], UserRole.LESSOR)
        tenants = self._create_users(options['tenants'], UserRole.TENANT)
        listings = self._create_listings(options['listings'], lessors, demo_photos)
        bookings = self._create_bookings(listings, tenants)
        reviews = self._create_reviews(bookings)
        views_created = self._create_view_history(listings, tenants)
        searches_created = self._create_search_history(tenants)
        photos_attached = sum(1 for listing in listings if listing.photos.exists())

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(lessors)} lessors, {len(tenants)} tenants, {len(listings)} listings '
            f'({photos_attached} with a photo), {len(bookings)} bookings, {len(reviews)} reviews, '
            f'{views_created} views, {searches_created} searches.'
        ))

    def _clear_seed_data(self):
        """Delete all previously seeded users; cascades to their listings, bookings, reviews and history."""
        seed_users = User.objects.filter(email__iendswith=f'@{SEED_EMAIL_DOMAIN}')
        count = seed_users.count()
        seed_users.delete()
        self.stdout.write(f'Cleared {count} previously seeded users and their related data.')

    def _create_users(self, count, role):
        """Create one fixed-credential demo account plus `count` random fake accounts for the given role."""
        users = [self._get_or_create_known_user(role)]
        for _ in range(count):
            username = f'{self.fake.user_name()}_{uuid.uuid4().hex[:6]}'
            email = f'{username}@{SEED_EMAIL_DOMAIN}'
            password = self.fake.password(length=12)
            users.append(UserService.create_user(email=email, password=password, username=username, role=role))
        return users

    def _get_or_create_known_user(self, role):
        """Return the fixed-credential demo account for the given role, creating it if missing."""
        if role == UserRole.LESSOR:
            email = env('SEED_DEMO_LESSOR_EMAIL', default=f'lessor@{SEED_EMAIL_DOMAIN}')
            password = env('SEED_DEMO_LESSOR_PASSWORD', default='demo-lessor-pass-1')
            username = 'demo_lessor'
        else:
            email = env('SEED_DEMO_TENANT_EMAIL', default=f'tenant@{SEED_EMAIL_DOMAIN}')
            password = env('SEED_DEMO_TENANT_PASSWORD', default='demo-tenant-pass-1')
            username = 'demo_tenant'

        existing = User.objects.filter(email=email).first()
        if existing:
            return existing
        return UserService.create_user(email=email, password=password, username=username, role=role)

    def _create_listings(self, count, lessors, demo_photos):
        """Create `count` listings with realistic German locations, owned by random lessors."""
        listings = []
        for i in range(count):
            city = random.choice(list(GERMAN_DISTRICTS.keys()))
            listing = Listing.objects.create(
                owner=random.choice(lessors),
                title=random.choice(LISTING_TITLES),
                description=self.fake.paragraph(nb_sentences=3),
                city=city,
                district=random.choice(GERMAN_DISTRICTS[city]),
                postal_code=self.fake_de.postcode(),
                price=random.randint(400, 3000),
                rooms=random.randint(1, 6),
                property_type=random.choice(PropertyType.values),
                is_active=(i % 6 != 0),
            )
            if demo_photos:
                self._attach_random_photo(listing, demo_photos)
            listings.append(listing)
        return listings

    def _discover_demo_photos(self):
        """Return the list of usable image files placed in DEMO_PHOTO_DIR, or an empty list if none exist."""
        if not DEMO_PHOTO_DIR.is_dir():
            return []
        return [
            path for path in DEMO_PHOTO_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in DEMO_PHOTO_EXTENSIONS
        ]

    def _attach_random_photo(self, listing, demo_photos):
        """Attach one randomly chosen demo photo to the listing as its cover image."""
        source = random.choice(demo_photos)
        photo = ListingPhoto(listing=listing, is_primary=True)
        with source.open('rb') as file_obj:
            photo.image.save(f'{uuid.uuid4().hex}{source.suffix.lower()}', File(file_obj), save=True)

    def _generate_booking_windows(self, count):
        """Yield `count` sequential, non-overlapping (start, end) date windows for one listing."""
        cursor = date.today() - timedelta(days=random.randint(0, 60))
        windows = []
        for _ in range(count):
            duration = random.randint(2, 14)
            start = cursor
            end = start + timedelta(days=duration)
            windows.append((start, end))
            cursor = end + timedelta(days=random.randint(1, 10))
        return windows

    def _weighted_status(self, is_past):
        """Pick a booking status, biased toward realistic outcomes for past or future stays."""
        if is_past:
            weights = {BookingStatus.CHECKED_IN: 55, BookingStatus.CANCELED: 25, BookingStatus.REJECTED: 20}
        else:
            weights = {BookingStatus.PENDING: 45, BookingStatus.CONFIRMED: 45, BookingStatus.CANCELED: 10}
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]

    def _create_bookings(self, listings, tenants):
        """Create 1-3 non-overlapping bookings per listing with a realistic status distribution."""
        bookings = []
        for listing in listings:
            for start, end in self._generate_booking_windows(random.randint(1, 3)):
                nights = (end - start).days
                booking_status = self._weighted_status(is_past=end <= date.today())
                rejection_reason = ''
                rejection_note = ''
                if booking_status == BookingStatus.REJECTED:
                    rejection_reason = random.choice(list(RejectionReason))
                    if rejection_reason == RejectionReason.OTHER:
                        rejection_note = self.fake.sentence()
                bookings.append(Booking.objects.create(
                    listing=listing,
                    tenant=random.choice(tenants),
                    start_date=start,
                    end_date=end,
                    price_per_night=listing.price,
                    total_price=listing.price * nights,
                    status=booking_status,
                    rejection_reason=rejection_reason or None,
                    rejection_note=rejection_note,
                ))
        return bookings

    def _create_reviews(self, bookings):
        """Create one review per checked-in booking, one at a time so rating signals recalculate."""
        reviews = []
        for booking in bookings:
            if booking.status != BookingStatus.CHECKED_IN:
                continue
            rating = random.choices([1, 2, 3, 4, 5], weights=[3, 7, 20, 35, 35])[0]
            reviews.append(Review.objects.create(
                listing=booking.listing,
                author=booking.tenant,
                booking=booking,
                rating=rating,
                comment=self.fake.sentence(nb_words=12),
            ))
        return reviews

    def _create_view_history(self, listings, tenants):
        """Record a handful of listing views per listing, some anonymous, through the real service."""
        total = 0
        viewers = tenants + [None, None]
        for listing in listings:
            for _ in range(random.randint(3, 15)):
                ViewHistoryService.record_view(listing=listing, user=random.choice(viewers))
                total += 1
        return total

    def _create_search_history(self, tenants):
        """Record realistic search keywords per tenant through the real service."""
        total = 0
        for tenant in tenants:
            for _ in range(random.randint(1, 4)):
                SearchHistoryService.record_search(user=tenant, keyword=random.choice(SEARCH_KEYWORDS))
                total += 1
        return total
