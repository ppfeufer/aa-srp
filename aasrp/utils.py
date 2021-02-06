# coding=utf-8

"""
utilities
"""

import logging
import os

from django.conf import settings
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from aasrp import __title__

from allianceauth.services.hooks import get_extension_logger


class LoggerAddTag(logging.LoggerAdapter):
    """
    add custom tag to a logger
    """

    def __init__(self, my_logger, prefix):
        super().__init__(my_logger, {})
        self.prefix = prefix

    def process(self, msg, kwargs):
        """
        process log items
        :param msg:
        :param kwargs:
        :return:
        """

        return "[%s] %s" % (self.prefix, msg), kwargs


logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def clean_setting(
    name: str,
    default_value: object,
    min_value: int = None,
    max_value: int = None,
    required_type: type = None,
):
    """cleans the input for a custom setting

    Will use `default_value` if settings does not exit or has the wrong type
    or is outside define boundaries (for int only)

    Need to define `required_type` if `default_value` is `None`

    Will assume `min_value` of 0 for int (can be overriden)

    Returns cleaned value for setting
    """

    if default_value is None and not required_type:
        raise ValueError(_("You must specify a required_type for None defaults"))

    if not required_type:
        required_type = type(default_value)

    if min_value is None and required_type == int:
        min_value = 0

    if not hasattr(settings, name):
        cleaned_value = default_value
    else:
        if (
            isinstance(getattr(settings, name), required_type)
            and (min_value is None or getattr(settings, name) >= min_value)
            and (max_value is None or getattr(settings, name) <= max_value)
        ):
            cleaned_value = getattr(settings, name)
        else:
            logger.warning(
                "You setting for {name} is not valid. Please correct it. "
                "Using default for now: {value}".format(name=name, value=default_value)
            )
            cleaned_value = default_value

    return cleaned_value


# Format for output of datetime for this app
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

format_html_lazy = lazy(format_html, str)


def get_swagger_spec_path() -> str:
    """
    returns the path to the current swagger spec file
    """

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "swagger.json")


def make_logger_prefix(tag: str):
    """
    creates a function to add logger prefix, which returns tag when used empty
    """

    return lambda text="": "{}{}".format(tag, (": " + text) if text else "")
