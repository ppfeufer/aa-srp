"""
App settings for the AA-SRP application.
This module defines configuration settings and utility functions for interacting with
Discord Proxy and checking the installation status of related Alliance Auth apps.
"""

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
    Check if the 'allianceauth-discordbot' app is installed and active.

    :return: True if the app is installed, False otherwise.
    :rtype: bool
    """

    return apps.is_installed(app_name="aadiscordbot")


def aa_discordnotify_installed() -> bool:
    """
    Check if the 'discordnotify' app is installed and active.

    :return: True if the app is installed, False otherwise.
    :rtype: bool
    """

    return apps.is_installed(app_name="discordnotify")


def discordproxy_installed() -> bool:
    """
    Check if the 'discordproxy' service is installed by attempting to import the DiscordClient.

    :return: True if the DiscordClient can be imported, False otherwise.
    :rtype: bool
    """

    try:
        # Third Party
        # pylint: disable=import-outside-toplevel, unused-import
        from discordproxy.client import DiscordClient  # noqa: F401
    except ModuleNotFoundError:
        return False

    return True
