"""
Some helper functions, so we don't mess up other files too much
"""

# Django
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership
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
    Get character name with alliance and corp ticker

    :param character:
    :type character:
    :param with_portrait:
    :type with_portrait:
    :param with_copy_icon:
    :type with_copy_icon:
    :param portrait_size:
    :type portrait_size:
    :param inline:
    :type inline:
    :return:
    :rtype:
    """

    try:
        character_name = character.character_name
    except AttributeError:
        character_name = _("Unknown character")

        return (
            "<span class='aasrp-character-portrait-character-name'>"
            f"{character_name}"
            "</span>"
        )

    character__corporation_ticker = (
        f"[{character.corporation_ticker}] " if character.corporation_ticker else ""
    )
    character__alliance_ticker = (
        f"{character.alliance_ticker} " if character.alliance_ticker else ""
    )
    character_name_formatted = (
        "<small class='text-muted'>"
        f"{character__alliance_ticker}{character__corporation_ticker}</small>"
        f"<br>{character_name}"
    )

    if with_copy_icon is True:
        title = _("Copy character name to clipboard")
        character_name_formatted += (
            "<i "
            'class="aa-srp-fa-icon copy-text-fa-icon fa-regular fa-copy ms-2" '
            f'data-clipboard-text="{character_name}" title="{title}" '
            'data-bs-tooltip="aa-srp"></i>'
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
            "<span class='aasrp-character-portrait-character-name'>"
            f"{character_name_formatted}"
            "</span>"
        )

    return return_value


def get_main_for_character(character: EveCharacter) -> EveCharacter | None:
    """
    Get the main character for a given eve character

    :param character:
    :type character:
    :return:
    :rtype:
    """

    try:
        userprofile = character.character_ownership.user.profile
    except (
        AttributeError,
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return None

    return userprofile.main_character


def get_user_for_character(character: EveCharacter) -> User:
    """
    Get the user for a character

    :param character:
    :type character:
    :return:
    :rtype:
    """

    try:
        userprofile = character.character_ownership.user.profile
    except (
        AttributeError,
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return get_sentinel_user()

    return userprofile.user
