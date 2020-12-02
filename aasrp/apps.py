# coding=utf-8

"""
app config
"""

from django.apps import AppConfig

from aasrp import __version__


class AaSrpConfig(AppConfig):
    """
    application config
    """

    name = "aasrp"
    label = "aasrp"
    verbose_name = "AA Ship Replacement v{}".format(__version__)
