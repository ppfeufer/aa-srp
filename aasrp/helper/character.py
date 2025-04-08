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
from aasrp.helper.icons import copy_to_clipboard_icon
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
            "<span class='aasrp-character-portrait-character-name d-inline-block align-middle'>"
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

    if with_copy_icon:
        title = _("Copy character name to clipboard")
        copy_icon = copy_to_clipboard_icon(data=character_name, title=title)
        character_name_formatted += f"<sup>{copy_icon}</sup>"

    if with_portrait:
        line_break = "<br>" if not inline else ""
        character_portrait_html = get_character_portrait_from_evecharacter(
            character=character, size=portrait_size, as_html=True
        )

        return (
            f"{character_portrait_html}{line_break}"
            "<span class='aasrp-character-portrait-character-name d-inline-block align-middle'>"
            f"{character_name_formatted}"
            "</span>"
        )

    return character_name_formatted


def get_main_for_character(character: EveCharacter) -> EveCharacter | None:
    """
    Get the main character for a given eve character

    :param character:
    :type character:
    :return:
    :rtype:
    """

    try:
        return character.character_ownership.user.profile.main_character
    except (
        AttributeError,
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return None


def get_user_for_character(character: EveCharacter) -> User:
    """
    Get the user for a character

    :param character:
    :type character:
    :return:
    :rtype:
    """

    try:
        return character.character_ownership.user.profile.user
    except (
        AttributeError,
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return get_sentinel_user()
