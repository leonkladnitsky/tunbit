from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations


def add_initial_data(apps, schema_editor):
    """
    Creates minimal initial data for the app.
    :param apps:
    :param schema_editor:
    :return:
    """
    if settings.DEBUG:
        user_model = apps.get_model('auth', 'User')
        u = user_model(
            username=settings.MASTER_USR,
            email=settings.MASTER_EML,
            password=make_password(settings.MASTER_PWD),
            first_name=settings.MASTER_FIRST,
            last_name=settings.MASTER_LAST,
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        u.save()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        ('contenttypes', '__latest__'),
        ('admin', '__latest__'),
        ('sessions', '__latest__'),
        ('messages', '__latest__'),
        ('staticfiles', '__latest__'),
    ]

    operations = [
        migrations.RunPython(add_initial_data),
    ]
