"""
App initialization module for the AA-SRP application.
This module defines metadata and constants for the Ship Replacement Program (SRP) app.
"""

# Django
from django.utils.translation import gettext_lazy as _

__version__ = "3.0.0"
__title__ = "Ship Replacement"
__title_translated__ = _("Ship Replacement")
__verbose_name__ = "Ship Replacement (SRP) for Alliance Auth"

__esi_compatibility_date__ = "2025-11-06"

__package_name__ = "aa-srp"
__app_name__ = "aasrp"
__app_name_verbose__ = "AA SRP"
__app_name_useragent__ = "AaSrp"

__github_url__ = f"https://github.com/ppfeufer/{__package_name__}"
