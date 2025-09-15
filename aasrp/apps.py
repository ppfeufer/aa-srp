"""
App configuration for the AA-SRP application.
This module defines the configuration class for the Ship Replacement Program (SRP) app.
"""

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# AA SRP
from aasrp import __version__


class AaSrpConfig(AppConfig):
    """
    Configuration class for the AA-SRP application.
    This class sets up the app's name, label, and verbose name for display in the Django admin interface.
    """

    # The full Python path to the application (e.g., 'aasrp').
    name = "aasrp"
    # A short, unique label for the application.
    label = "aasrp"
    # The human-readable name of the application, including its version.
    # Translators: This is the app name and version, which will appear in the Django Backend
    verbose_name = _(f"Ship Replacement v{__version__}")
