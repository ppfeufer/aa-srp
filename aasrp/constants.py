"""
Constants for the AA-SRP application.
This module defines various constants used throughout the application, including
user agent strings, notification messages, killboard URLs, and Discord embed colors.
"""

# Standard Library
from enum import Enum

# Third Party
from requests import __version__ as requests_version

# AA SRP
from aasrp import __app_name_useragent__, __github_url__
from aasrp import __version__ as app_version

# All internal URLs need to start with this prefix
INTERNAL_URL_PREFIX = "-"


class UserAgent(Enum):
    """
    Enumeration for UserAgent strings.
    Defines the user agent string for HTTP requests made by the application.
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
        "requires_trailing_slash": True,
    },
    "EveTools": {
        "base_url": "https://kb.evetools.org",
        "base_url_regex": r"^http[s]?:\/\/kb\.evetools\.org\/",
        "killmail_url_regex": r"^http[s]?:\/\/kb\.evetools\.org\/kill\/\d+",
        "requires_trailing_slash": False,
    },
    "EVE-KILL": {
        "base_url": "https://eve-kill.com",
        "base_url_regex": r"^http[s]?:\/\/eve-kill\.com\/",
        "killmail_url_regex": r"^http[s]?:\/\/eve-kill\.com\/kill\/\d+",
        "requires_trailing_slash": False,
    },
}


class DiscordEmbedColor(Enum):
    """
    Enumeration for Discord embed colors.
    Defines color codes for different types of messages in Discord embeds.
    """

    INFO = 0x5BC0DE
    SUCCESS = 0x5CB85C
    WARNING = 0xF0AD4E
    DANGER = 0xD9534F


DISCORD_EMBED_COLOR_MAP = {
    color.name.lower(): color.value for color in DiscordEmbedColor
}
