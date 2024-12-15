"""
Constants
"""

# Third Party
from requests.__version__ import __version__ as requests_version

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from esi import __version__ as esi_version

# AA SRP
from aasrp import __version__

APP_NAME = "aa-srp"
GITHUB_URL = f"https://github.com/ppfeufer/{APP_NAME}"
USER_AGENT_ESI = f"{APP_NAME}/{__version__} +{GITHUB_URL} via django-esi/{esi_version}"
USER_AGENT_REQUESTS = (
    f"{APP_NAME}/{__version__} +{GITHUB_URL} via requests/{requests_version}"
)


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
