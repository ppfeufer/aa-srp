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
