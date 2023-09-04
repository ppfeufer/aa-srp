"""
Template tag

Do some useful stuff with a User object
"""

# Django
from django.contrib.auth.models import User
from django.template.defaulttags import register

# AA SRP
from aasrp.helper.character import get_main_character_from_user


@register.filter
def main_character_name(user: User) -> str:
    """
    Get the users main character name, or return the username if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return ""

    return get_main_character_from_user(user=user)


@register.filter
def main_character_id(user: User) -> int:
    """
    Get the users main character id, or return 1 if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return 1

    try:
        return_value = user.profile.main_character.character_id
    except AttributeError:
        return_value = 1

    return return_value


@register.filter
def main_character_corporation_name(user: User) -> str:
    """
    Get the users main character corporation name,
    or an empty string if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return ""

    try:
        return_value = user.profile.main_character.corporation_name
    except AttributeError:
        return_value = ""

    return return_value


@register.filter
def main_character_corporation_id(user: User) -> int:
    """
    Get the users main character corporation id, or 1 if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return 1

    try:
        return_value = user.profile.main_character.corporation_id
    except AttributeError:
        return_value = 1

    return return_value


@register.filter
def main_character_alliance_name(user: User) -> str:
    """
    Get the users main character alliance name, or an empty string if no main character

    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        return ""

    try:
        return_value = user.profile.main_character.alliance_name
    except AttributeError:
        return_value = ""

    return return_value


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
        return_value = user.profile.main_character.alliance_id

        # Check if the user is in an alliance
        try:
            return_value = int(return_value)
        except Exception:  # pylint: disable=broad-exception-caught
            return_value = 1
    except AttributeError:
        return_value = 1

    return return_value
