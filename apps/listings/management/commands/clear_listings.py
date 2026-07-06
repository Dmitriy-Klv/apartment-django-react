from django.conf import settings
from django.core.management.base import BaseCommand

from apps.listings.models import Listing, ListingPhoto


class Command(BaseCommand):
    help = 'Permanently delete all listings and their cascaded bookings, reviews, photos and view history.'

    def add_arguments(self, parser):
        """Register the CLI options for this command."""
        parser.add_argument('--yes', action='store_true', help='Skip the interactive confirmation prompt.')

    def handle(self, *args, **options):
        """Delete every listing after an explicit confirmation, then remove orphaned photo files from disk."""
        count = Listing.objects.count()
        if count == 0:
            self.stdout.write('No listings found, nothing to delete.')
            return

        if not options['yes']:
            answer = input(
                f'This will permanently delete {count} listing(s) and all their bookings, '
                'reviews, photos and view history. Type "yes" to continue: '
            )
            if answer.strip().lower() != 'yes':
                self.stdout.write(self.style.WARNING('Aborted, nothing was deleted.'))
                return

        photo_names = list(ListingPhoto.objects.values_list('image', flat=True))
        _, deleted_per_model = Listing.objects.all().delete()

        removed_files = 0
        for name in photo_names:
            file_path = settings.MEDIA_ROOT / name
            if file_path.is_file():
                file_path.unlink()
                removed_files += 1

        self.stdout.write(self.style.SUCCESS(
            f'Deleted {count} listing(s) and {removed_files} photo file(s) from disk.'
        ))
        for model_label, model_count in sorted(deleted_per_model.items()):
            self.stdout.write(f'  {model_label}: {model_count}')
