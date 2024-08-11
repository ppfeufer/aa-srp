"""
Constants
"""

# Django
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# AA SRP
from aasrp import __version__

VERBOSE_NAME = "AA-SRP - A ship replacement module for Alliance Auth"

verbose_name_slugified: str = slugify(value=VERBOSE_NAME, allow_unicode=True)
github_url: str = "https://github.com/ppfeufer/aa-srp"
USERAGENT = f"{verbose_name_slugified} v{__version__} {github_url}"


SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE = _(
    "If you have any questions regarding your SRP request, feel free to contact your "
    "request reviser.\nPlease make sure to always add the SRP code and the "
    "request code with your inquiry."
)

# Killboard URLs and regex
KILLBOARD_DATA = {
    "zKillboard": {
        "base_url": "https://zkillboard.com/",
        "api_url": "https://zkillboard.com/api/",
        "base_url_regex": r"^http[s]?:\/\/zkillboard\.com\/",
        "killmail_url_regex": r"^http[s]?:\/\/zkillboard\.com\/kill\/\d+\/",
    },
    "EveTools": {
        "base_url": "https://kb.evetools.org/",
        "base_url_regex": r"^http[s]?:\/\/kb\.evetools\.org\/",
        "killmail_url_regex": r"^http[s]?:\/\/kb\.evetools\.org\/kill\/\d+",
    },
    "EVE-KILL": {
        "base_url": "https://eve-kill.com/",
        "base_url_regex": r"^http[s]?:\/\/eve-kill\.com\/",
        "killmail_url_regex": r"^http[s]?:\/\/eve-kill\.com\/kill\/\d+",
    },
}


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
