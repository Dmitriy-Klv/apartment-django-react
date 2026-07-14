from django.db import migrations, models


def backfill_deleted_at(apps, schema_editor):
    """Approximate the deletion timestamp of already soft-deleted listings.

    The exact moment of deletion was never recorded before this migration, so
    `updated_at` (last modified time) is used as the closest available proxy.
    """
    Listing = apps.get_model('listings', 'Listing')
    Listing.objects.filter(is_deleted=True).update(deleted_at=models.F('updated_at'))


def noop_reverse(apps, schema_editor):
    """No reverse action; re-adding the boolean field is handled by RemoveField's reversal."""


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0004_alter_listing_price_alter_listing_rooms"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_deleted_at, noop_reverse),
        migrations.RemoveField(
            model_name="listing",
            name="is_deleted",
        ),
    ]
