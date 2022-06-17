"""
App config
"""

# Django
from django.apps import AppConfig

# AA SRP
from aasrp import __version__


class AaSrpConfig(AppConfig):
    """
    Application config
    """

    name = "aasrp"
    label = "aasrp"
    verbose_name = f"AA Ship Replacement v{__version__}"
