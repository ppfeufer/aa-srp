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


def allianceauth_discordbot_installed():
    """
    Check if allianceauth-dicordbot is installed and active
    :return:
    """

    return apps.is_installed("aadiscordbot")


def aa_discordnotify_installed():
    """
    Check if allianceauth-dicordbot is installed and active
    :return:
    """

    return apps.is_installed("discordnotify")
