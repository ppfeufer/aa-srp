"""
This module provides helper functions for working with Eve characters.
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
    Generate a formatted string for an Eve character's name, including optional alliance and corporation tickers,
    and optionally include a portrait image and/or a copy-to-clipboard icon.

    :param character: The Eve character object containing character details.
    :type character: EveCharacter
    :param with_portrait: Whether to include the character's portrait in the output.
    :type with_portrait: bool, optional
    :param with_copy_icon: Whether to include a copy-to-clipboard icon for the character's name.
    :type with_copy_icon: bool, optional
    :param portrait_size: The size of the portrait image, if included.
    :type portrait_size: int, optional
    :param inline: Whether the portrait and name should be displayed inline.
    :type inline: bool, optional
    :return: A formatted HTML string representing the character's name and optional elements.
    :rtype: str
    """

    # Get the character's name, defaulting to "Unknown character" if not available
    character_name = getattr(character, "character_name", _("Unknown character"))

    # If the character name is unknown, return a simple HTML span with the name
    if character_name == _("Unknown character"):
        return (
            "<span class='aasrp-character-portrait-character-name d-inline-block align-middle'>"
            f"{character_name}"
            "</span>"
        )

    # Format the corporation and alliance tickers, if available
    corporation_ticker = (
        f"[{character.corporation_ticker}] " if character.corporation_ticker else ""
    )
    alliance_ticker = (
        f"{character.alliance_ticker} " if character.alliance_ticker else ""
    )

    # Combine the tickers and character name into a formatted string
    character_name_formatted = (
        f"<small class='text-muted'>{alliance_ticker}{corporation_ticker}</small>"
        f"<br>{character_name}"
    )

    # Add a copy-to-clipboard icon if requested
    if with_copy_icon:
        copy_icon = copy_to_clipboard_icon(
            data=character_name, title=_("Copy character name to clipboard")
        )
        character_name_formatted += f"<sup>{copy_icon}</sup>"

    # Add the character's portrait if requested
    if with_portrait:
        line_break = "<br>" if not inline else ""
        portrait_html = get_character_portrait_from_evecharacter(
            character, size=portrait_size, as_html=True
        )

        return f"{portrait_html}{line_break}<span class='aasrp-character-portrait-character-name d-inline-block align-middle'>{character_name_formatted}</span>"

    # Return the formatted character name
    return character_name_formatted


def get_main_for_character(character: EveCharacter) -> EveCharacter | None:
    """
    Retrieve the main character associated with a given Eve character.

    This function attempts to access the main character linked to the provided Eve character
    through the character's ownership and user profile. If any of the required relationships
    or attributes are missing, it returns `None`.

    :param character: The Eve character object for which to find the main character.
    :type character: EveCharacter
    :return: The main character associated with the given Eve character, or `None` if not found.
    :rtype: EveCharacter | None
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
    Retrieve the user associated with a given Eve character.

    This function attempts to access the user linked to the provided Eve character
    through the character's ownership and user profile. If any of the required relationships
    or attributes are missing, it returns a sentinel user.

    :param character: The Eve character object for which to find the associated user.
    :type character: EveCharacter
    :return: The user associated with the given Eve character, or a sentinel user if not found.
    :rtype: User
    """

    try:
        return character.character_ownership.user.profile.user
    except (
        AttributeError,
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return get_sentinel_user()
