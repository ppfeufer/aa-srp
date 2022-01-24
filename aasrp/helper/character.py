"""
some helper functions
so we don't mess up other files too much
"""

# Django
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# AA SRP
from aasrp.helper.eve_images import get_character_portrait_from_evecharacter
from aasrp.models import get_sentinel_user


def get_formatted_character_name(
    character: EveCharacter,
    with_portrait: bool = False,
    with_copy_icon: bool = False,
    portrait_size: int = 32,
    inline: bool = True,
) -> str:
    """
    get character name with alliance and corp ticker
    :param character:
    :param with_portrait:
    :param with_copy_icon:
    :param portrait_size:
    :param inline:
    """

    try:
        character_name = character.character_name
    except AttributeError:
        character_name = _("Unknown Character")

        return (
            f"<span class='aasrp-character-portrait-character-name'>"
            f"{character_name}"
            f"</span>"
        )
    else:
        character__corporation_ticker = (
            f"[{character.corporation_ticker}] " if character.corporation_ticker else ""
        )
        character__alliance_ticker = (
            f"{character.alliance_ticker} " if character.alliance_ticker else ""
        )
        character_name_formatted = (
            f"<small class='text-muted'>"
            f"{character__alliance_ticker}{character__corporation_ticker}</small>"
            f"<br>{character_name}"
        )

        if with_copy_icon is True:
            title = _("Copy character name to clipboard")
            character_name_formatted += (
                f"<i "
                f'class="aa-srp-fa-icon aa-srp-fa-icon-right copy-text-fa-icon far fa-copy" '
                f'data-clipboard-text="{character_name}" title="{title}"></i>'
            )

        return_value = character_name_formatted

        if with_portrait is True:
            line_break = ""
            if inline is False:
                line_break = "<br>"

            character_portrait_html = get_character_portrait_from_evecharacter(
                character=character, size=portrait_size, as_html=True
            )

            return_value = (
                f"{character_portrait_html}{line_break}"
                f"<span class='aasrp-character-portrait-character-name'>"
                f"{character_name_formatted}"
                f"</span>"
            )

    return return_value


def get_main_for_character(character: EveCharacter) -> EveCharacter:
    """
    get the main character for a given eve character
    :param character:
    """

    return_value = None

    if character.userprofile:
        return_value = character.userprofile.main_character

    return return_value


def get_user_for_character(character: EveCharacter) -> User:
    """
    get the user for a character
    :param character:
    :return:
    """

    if character.userprofile is None:
        return_value = get_sentinel_user()
    else:
        return_value = character.userprofile.user

    return return_value


def get_main_character_from_user(user: User) -> str:
    """
    Get the main character from a user
    :param user:
    :type user:
    :return:
    :rtype:
    """

    user_main_character = user.username

    try:
        user_profile = user.profile
        user_main_character = user_profile.main_character.character_name
    except AttributeError:
        pass

    return user_main_character
