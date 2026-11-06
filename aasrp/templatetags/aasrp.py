"""
AA SRP - Template Tags

This module provides custom Django template tags for the AA SRP application.
"""

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.template.defaulttags import register
from django.utils.safestring import mark_safe

# Alliance Auth
from allianceauth.authentication.models import User
from allianceauth.framework.api.user import get_main_character_name_from_user
from allianceauth.services.hooks import get_extension_logger

# AA SRP
from aasrp.helper.icons import dashboard_action_icons
from aasrp.models import SrpLink
from aasrp.providers.applogger import AppLogger

# Initialize a logger with a custom tag for the AA SRP module
logger = AppLogger(my_logger=get_extension_logger(__name__))


@register.filter
def main_character_name(user: User) -> str:
    """
    Get the user's main character name, or return the username if no main character is set.

    :param user: The user object to retrieve the main character name from.
    :type user: User
    :return: The main character name or the username if no main character exists.
    :rtype: str
    """

    return get_main_character_name_from_user(user=user)


@register.filter
def main_character_id(user: User) -> int:
    """
    Get the user's main character ID, or return 1 if no main character is set.

    :param user: The user object to retrieve the main character ID from.
    :type user: User
    :return: The main character ID or 1 if no main character exists.
    :rtype: int
    """

    if user and hasattr(user.profile.main_character, "character_id"):
        return user.profile.main_character.character_id

    return 1


@register.filter
def main_character_corporation_name(user: User) -> str:
    """
    Get the user's main character corporation name, or return an empty string if no main character is set.

    :param user: The user object to retrieve the corporation name from.
    :type user: User
    :return: The main character's corporation name or an empty string if no main character exists.
    :rtype: str
    """

    if user and hasattr(user.profile.main_character, "corporation_name"):
        return user.profile.main_character.corporation_name

    return ""


@register.filter
def main_character_corporation_id(user: User) -> int:
    """
    Get the user's main character corporation ID, or return 1 if no main character is set.

    :param user: The user object to retrieve the corporation ID from.
    :type user: User
    :return: The main character's corporation ID or 1 if no main character exists.
    :rtype: int
    """

    if user and hasattr(user.profile.main_character, "corporation_id"):
        return user.profile.main_character.corporation_id

    return 1


@register.filter
def main_character_alliance_name(user: User) -> str:
    """
    Get the user's main character alliance name, or return an empty string if no main character is set.

    :param user: The user object to retrieve the alliance name from.
    :type user: User
    :return: The main character's alliance name or an empty string if no main character exists.
    :rtype: str
    """

    return getattr(user.profile.main_character, "alliance_name", "") if user else ""


@register.filter
def main_character_alliance_id(user: User) -> int:
    """
    Get the user's main character alliance ID, or return 1 if no main character is set.

    :param user: The user object to retrieve the alliance ID from.
    :type user: User
    :return: The main character's alliance ID or 1 if no main character exists.
    :rtype: int
    """

    if user is None:
        return 1

    try:
        return_value = int(user.profile.main_character.alliance_id)
    except (AttributeError, ValueError, TypeError):
        return_value = 1

    return return_value


@register.filter
def srp_link_actions(srp_link: SrpLink, request: WSGIRequest) -> str:
    """
    Get the HTML for the actions available for a given SRP link.

    {{ srp_link|srp_link_actions:request }}

    :param srp_link: The SRP link object to retrieve actions for.
    :type srp_link: SrpLink
    :param request: The WSGIRequest object representing the current request.
    :type request: WSGIRequest
    :return: The HTML string representing the actions for the SRP link.
    :rtype: str
    """

    if not srp_link:
        return ""

    # Return the HTML for the dashboard action icons for the given SRP link
    return mark_safe(dashboard_action_icons(request=request, srp_link=srp_link))
