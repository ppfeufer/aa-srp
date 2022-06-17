"""
Utilities
"""

# Django
from django.conf import settings
from django.utils.functional import lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def clean_setting(
    name: str,
    default_value: object,
    min_value: int = None,
    max_value: int = None,
    required_type: type = None,
):
    """
    Cleans the input for a custom setting

    Will use `default_value` if settings does not exit or has the wrong type
    or is outside define boundaries (for int only)

    Need to define `required_type` if `default_value` is `None`

    Will assume `min_value` of 0 for int (can be overridden)

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
                f"You setting for {name} is not valid. Please correct it. "
                f"Using default for now: {default_value}"
            )
            cleaned_value = default_value

    return cleaned_value


# Format for output of datetime for this app
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

format_html_lazy = lazy(format_html, str)
