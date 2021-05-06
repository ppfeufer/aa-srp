"""
app config
"""

from django.apps import AppConfig

from aasrp import __version__


class AaSrpConfig(AppConfig):
    """
    application config
    """

    name = "aasrp"
    label = "aasrp"
    verbose_name = f"AA Ship Replacement v{__version__}"
