"""
our app setting
"""

# Django
from django.apps import apps

# AA SRP
from aasrp.utils import clean_setting

# AA-GDPR
AVOID_CDN = clean_setting("AVOID_CDN", False)

# SRP Team Discord Channel
AASRP_SRP_TEAM_DISCORD_CHANNEL = clean_setting(
    name="AASRP_SRP_TEAM_DISCORD_CHANNEL", default_value=None, required_type=int
)


def avoid_cdn() -> bool:
    """
    check if we should aviod CDN usage
    :return: bool
    """

    return AVOID_CDN


def allianceauth_discordbot_active():
    """
    check if allianceauth-dicordbot is installed and active
    :return:
    """

    return apps.is_installed("aadiscordbot")


def aa_discordnotify_active():
    """
    check if allianceauth-dicordbot is installed and active
    :return:
    """

    return apps.is_installed("discordnotify")
