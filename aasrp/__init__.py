# coding=utf-8

"""
a couple of variable to use throughout the app
"""

from django.utils.text import slugify

default_app_config: str = "aasrp.apps.AaSrpConfig"

__version__ = "0.1.0-beta.9"
__title__ = "Ship Replacement"
__verbose_name__ = "AA-SRP - A ship replacement module for Alliance Auth"
__user_agent__ = "{verbose_name} - v{version} - {github_url}".format(
    verbose_name=slugify(__verbose_name__, allow_unicode=True),
    version=__version__,
    github_url="https://github.com/ppfeufer/aa-srp",
)
