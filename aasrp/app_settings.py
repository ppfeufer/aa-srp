"""
App settings
"""

# Django
from django.apps import apps


def allianceauth_discordbot_installed() -> bool:
    """
    Check if allianceauth-discordbot is installed and active

    :return:
    :rtype:
    """

    return apps.is_installed("aadiscordbot")


def aa_discordnotify_installed() -> bool:
    """
    Check if allianceauth-discordbot is installed and active

    :return:
    :rtype:
    """

    return apps.is_installed("discordnotify")


def discordproxy_installed() -> bool:
    """
    Check if discordproxy is installed by trying to import the DiscordClient

    :return:
    :rtype:
    """

    try:
        # Third Party
        # pylint: disable=import-outside-toplevel
        from discordproxy.client import DiscordClient  # noqa: F401
    except ModuleNotFoundError:
        return False

    return True
