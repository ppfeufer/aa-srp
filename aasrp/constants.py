# coding=utf-8

"""
constants
"""

from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from aasrp import __version__

VERBOSE_NAME = "AA-SRP - A ship replacement module for Alliance Auth"
USERAGENT = "{verbose_name} v{version} {github_url}".format(
    verbose_name=slugify(VERBOSE_NAME, allow_unicode=True),
    version=__version__,
    github_url="https://github.com/ppfeufer/aa-srp",
)
EVE_CATEGORY_ID_SHIP = 6

SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE = _(
    "If you have any questions regarding your SRP request, feel free to contact your "
    "request reviser.\nPlease make sure to always add the SRP-Code and the "
    "Request-Code with your inquiry."
)
