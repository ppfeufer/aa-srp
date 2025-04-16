"""
App config
"""

# Django
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

# AA SRP
from aasrp import __version__


class AaSrpConfig(AppConfig):
    """
    Application config
    """

    name = "aasrp"
    label = "aasrp"
    # Translators: This is the app name and version, which will appear in the Django Backend
    verbose_name = _(f"Ship Replacement v{__version__}")
