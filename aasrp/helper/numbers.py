"""
Helper functions for number formatting and localization.

This module provides utility functions for formatting numbers and localizing them
for display in Django templates. It includes support for specifying the number of
decimal places to display.
"""

# Django
from django.template.defaultfilters import floatformat


def l10n_number_format(value: float, number_of_decimals: int = 0) -> str:
    """
    Localize a number for display in the template.

    This function formats a given number to a specified number of decimal places
    and localizes it for display in Django templates.

    :param value: The number to be localized.
    :type value: float
    :param number_of_decimals: The number of decimal places to display.
    :type number_of_decimals: int
    :return: The localized number as a string.
    :rtype: str
    """

    return floatformat(text=value, arg=f"{number_of_decimals}g")
