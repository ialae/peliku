"""Root pytest configuration for the Peliku project."""

import django
from django.conf import settings


def pytest_configure():
    """Configure Django settings for pytest."""
    settings.DJANGO_SETTINGS_MODULE = "peliku.settings"
    django.setup()
