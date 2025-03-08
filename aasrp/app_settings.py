"""
App settings
"""

# Standard Library
from re import RegexFlag

# Django
from django.apps import apps
from django.conf import settings

# Port used to communicate with Discord Proxy
DISCORDPROXY_PORT = getattr(settings, "DISCORDPROXY_PORT", 50051)

# Host used to communicate with Discord Proxy
DISCORDPROXY_HOST = getattr(settings, "DISCORDPROXY_HOST", "localhost")

# Timeout for Discord Proxy communication
DISCORDPROXY_TIMEOUT = getattr(settings, "DISCORDPROXY_TIMEOUT", 300)


def allianceauth_discordbot_installed() -> bool:
    """
    Check if allianceauth-discordbot is installed and active

    :return:
    :rtype:
    """

    return apps.is_installed(app_name="aadiscordbot")


def aa_discordnotify_installed() -> bool:
    """
    Check if allianceauth-discordbot is installed and active

    :return:
    :rtype:
    """

    return apps.is_installed(app_name="discordnotify")


def discordproxy_installed() -> bool:
    """
    Check if discordproxy is installed by trying to import the DiscordClient

    :return:
    :rtype:
    """

    try:
        # Third Party
        # pylint: disable=import-outside-toplevel, unused-import
        from discordproxy.client import DiscordClient  # noqa: F401
    except ModuleNotFoundError:
        return False

    return True


def debug_enabled() -> RegexFlag:
    """
    Check if DEBUG is enabled

    :return:
    :rtype:
    """

    return settings.DEBUG
