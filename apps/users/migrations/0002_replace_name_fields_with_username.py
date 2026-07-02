import django.contrib.auth.validators
from django.db import migrations, models


def populate_username(apps, schema_editor):
    """Backfill username from the email local part, de-duplicating collisions."""
    User = apps.get_model('users', 'User')
    seen = set()
    for user in User.objects.all():
        base = user.email.split('@')[0] or f'user{user.id}'
        candidate = base
        suffix = 1
        while candidate in seen or User.objects.filter(username=candidate).exclude(pk=user.pk).exists():
            candidate = f'{base}{suffix}'
            suffix += 1
        seen.add(candidate)
        user.username = candidate
        user.save(update_fields=['username'])


def reverse_populate_username(apps, schema_editor):
    """No-op: first_name/last_name values cannot be recovered from username."""


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.RunPython(populate_username, reverse_populate_username),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(
                max_length=150,
                unique=True,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
            ),
        ),
        migrations.RemoveField(
            model_name='user',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
    ]
