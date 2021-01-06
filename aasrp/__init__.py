# coding=utf-8

"""
a couple of variable to use throughout the app
"""

default_app_config: str = "aasrp.apps.AaSrpConfig"

__version__ = "0.1.0-beta.8"
__title__ = "Ship Replacement"
__verbose_name__ = "AA-SRP - A ship replacement module for Alliance Auth"
__user_agent__ = "{verbose_name} - v{version} - {github_url}".format(
    verbose_name=__verbose_name__,
    version=__version__,
    github_url="https://github.com/ppfeufer/aa-srp",
)
