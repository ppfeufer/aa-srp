"""
App settings
"""

# Django
from django.apps import apps

# AA SRP
from aasrp.utils import clean_setting

# SRP Team Discord Channel
AASRP_SRP_TEAM_DISCORD_CHANNEL = clean_setting(
    name="AASRP_SRP_TEAM_DISCORD_CHANNEL", default_value=None, required_type=int
)


def allianceauth_discordbot_installed() -> bool:
    """
    Check if allianceauth-discordbot is installed and active
    :return:
    """

    return apps.is_installed("aadiscordbot")


def aa_discordnotify_installed() -> bool:
    """
    Check if allianceauth-discordbot is installed and active
    :return:
    """

    return apps.is_installed("discordnotify")


def discordproxy_installed() -> bool:
    """
    Check if discordproxy is installed by trying to import the DiscordClient
    :return:
    """

    try:
        # Third Party
        from discordproxy.client import DiscordClient  # noqa: F401
    except ModuleNotFoundError:
        return False
    else:
        return True
