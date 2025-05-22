"""
Versioned static URLs to break browser caches when changing the app version
"""

# Django
from django.contrib.auth.models import User
from django.template.defaulttags import register

# Alliance Auth
from allianceauth.framework.api.user import get_main_character_name_from_user
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


@register.filter
def main_character_name(user: User) -> str:
    """
    Get the users main character name, or return the username if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    return get_main_character_name_from_user(user=user)


@register.filter
def main_character_id(user: User) -> int:
    """
    Get the users main character id, or return 1 if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user and hasattr(user.profile.main_character, "character_id"):
        return user.profile.main_character.character_id

    return 1


@register.filter
def main_character_corporation_name(user: User) -> str:
    """
    Get the users main character corporation name, or an empty string if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user and hasattr(user.profile.main_character, "corporation_name"):
        return user.profile.main_character.corporation_name

    return ""


@register.filter
def main_character_corporation_id(user: User) -> int:
    """
    Get the users main character corporation id, or 1 if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user and hasattr(user.profile.main_character, "corporation_id"):
        return user.profile.main_character.corporation_id

    return 1


@register.filter
def main_character_alliance_name(user: User) -> str:
    """
    Get the users main character alliance name, or an empty string if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    return getattr(user.profile.main_character, "alliance_name", "") if user else ""


@register.filter
def main_character_alliance_id(user: User) -> int:
    """
    Get the users main character alliance id, or 1 if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return 1

    try:
        return_value = int(user.profile.main_character.alliance_id)
    except (AttributeError, ValueError, TypeError):
        return_value = 1

    return return_value
