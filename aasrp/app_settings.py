# coding=utf-8

"""
our app setting
"""

import re

from django.conf import settings

from aasrp.utils import clean_setting

# AA-GDPR
AVOID_CDN = clean_setting("AVOID_CDN", False)

# SRP Team Discord Channel
AASRP_SRP_TEAM_DISCORD_CHANNEL = clean_setting(
    name="AASRP_SRP_TEAM_DISCORD_CHANNEL", default_value=None, required_type=int
)


def get_site_url() -> str:  # regex sso url
    """
    get the site url
    :return: string
    """
    regex = r"^(.+)\/s.+"
    matches = re.finditer(regex, settings.ESI_SSO_CALLBACK_URL, re.MULTILINE)
    url = "http://"

    for match in matches:
        url = match.groups()[0]  # first match

    return url


def avoid_cdn() -> bool:
    """
    check if we should aviod CDN usage
    :return: bool
    """
    return AVOID_CDN


def discord_bot_active():
    """
    check if allianceauth-dicordbot is installed and active
    :return:
    """

    return "aadiscordbot" in settings.INSTALLED_APPS
