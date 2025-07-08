"""
Constants
"""

# Standard Library
from enum import Enum

# Third Party
from requests.__version__ import __version__ as requests_version

# AA SRP
from aasrp import __app_name_useragent__, __github_url__
from aasrp import __version__ as app_version


class UserAgent(Enum):
    """
    UserAgent
    """

    REQUESTS = f"{__app_name_useragent__}/{app_version} (+{__github_url__}) requests/{requests_version}"


SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE = (
    "If you have any questions regarding your SRP request, feel free to contact your "
    "request reviser. Please make sure to always add the SRP code and the "
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


class DiscordEmbedColor(Enum):
    """
    Discord embed colors
    """

    INFO = 0x5BC0DE
    SUCCESS = 0x5CB85C
    WARNING = 0xF0AD4E
    DANGER = 0xD9534F


DISCORD_EMBED_COLOR_MAP = {
    "info": DiscordEmbedColor.INFO.value,
    "success": DiscordEmbedColor.SUCCESS.value,
    "warning": DiscordEmbedColor.WARNING.value,
    "danger": DiscordEmbedColor.DANGER.value,
}
