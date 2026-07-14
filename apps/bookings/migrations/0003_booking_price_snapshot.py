from decimal import Decimal

import django.core.validators
from django.db import migrations, models


def backfill_booking_prices(apps, schema_editor):
    """Snapshot each existing booking's price from its listing's current price.

    The original price agreed at booking time is unrecoverable for rows created
    before this migration, so the listing's current price is used as the closest
    available approximation.
    """
    Booking = apps.get_model('bookings', 'Booking')
    for booking in Booking.objects.select_related('listing').all():
        nights = (booking.end_date - booking.start_date).days
        booking.price_per_night = booking.listing.price
        booking.total_price = booking.listing.price * nights
        booking.save(update_fields=['price_per_night', 'total_price'])


def noop_reverse(apps, schema_editor):
    """No reverse action; dropping the columns is handled by the field removal itself."""


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0002_booking_booking_end_date_after_start_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="price_per_night",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="total_price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.RunPython(backfill_booking_prices, noop_reverse),
        migrations.AlterField(
            model_name="booking",
            name="price_per_night",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AlterField(
            model_name="booking",
            name="total_price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
    ]
