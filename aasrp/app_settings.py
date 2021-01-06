# coding=utf-8

"""
our app setting
"""

import re

from django.conf import settings

from aasrp.utils import clean_setting

# AA-GDPR
AVOID_CDN = clean_setting("AVOID_CDN", False)


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
