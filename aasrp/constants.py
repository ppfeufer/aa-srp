"""
Constants
"""

# Django
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# AA SRP
from aasrp import __version__

VERBOSE_NAME = "AA-SRP - A ship replacement module for Alliance Auth"

verbose_name_slugified: str = slugify(VERBOSE_NAME, allow_unicode=True)
github_url: str = "https://github.com/ppfeufer/aa-srp"
USERAGENT = f"{verbose_name_slugified} v{__version__} {github_url}"

EVE_CATEGORY_ID_SHIP = 6

SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE = _(
    "If you have any questions regarding your SRP request, feel free to contact your "
    "request reviser.\nPlease make sure to always add the SRP-Code and the "
    "Request-Code with your inquiry."
)

# zKillboard - https://zkillboard.com/
ZKILLBOARD_BASE_URL = "https://zkillboard.com/"
ZKILLBOARD_API_URL = "https://zkillboard.com/api/"
ZKILLBOARD_BASE_URL_REGEX = r"^http[s]?:\/\/zkillboard\.com\/"
ZKILLBOARD_KILLMAIL_URL_REGEX = r"^http[s]?:\/\/zkillboard\.com\/kill\/\d+\/"

# EveTools Killboard - https://kb.evetools.org/
EVETOOLS_KILLBOARD_BASE_URL = "https://kb.evetools.org/"
EVETOOLS_KILLBOARD_BASE_URL_REGEX = r"^http[s]?:\/\/kb\.evetools\.org\/"
EVETOOLS_KILLBOARD_KILLMAIL_URL_REGEX = r"^http[s]?:\/\/kb\.evetools\.org\/kill\/\d+"

# Embed colors
DISCORD_EMBED_COLOR_INFO = 0x5BC0DE
DISCORD_EMBED_COLOR_SUCCESS = 0x5CB85C
DISCORD_EMBED_COLOR_WARNING = 0xF0AD4E
DISCORD_EMBED_COLOR_DANGER = 0xD9534F

DISCORD_EMBED_COLOR_MAP = {
    "info": DISCORD_EMBED_COLOR_INFO,
    "success": DISCORD_EMBED_COLOR_SUCCESS,
    "warning": DISCORD_EMBED_COLOR_WARNING,
    "danger": DISCORD_EMBED_COLOR_DANGER,
}
