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
            "<span class='aasrp-character-portrait-character-name'>"
            f"{character_name}"
            "</span>"
        )
    else:
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
                'class="aa-srp-fa-icon aa-srp-fa-icon-right copy-text-fa-icon far fa-copy" '
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
                "<span class='aasrp-character-portrait-character-name'>"
                f"{character_name_formatted}"
                "</span>"
            )

    return return_value


def get_main_for_character(character: EveCharacter) -> EveCharacter:
    """
    Get the main character for a given eve character
    :param character:
    """

    try:
        userprofile = character.character_ownership.user.profile
    except (
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return_value = None
    else:
        return_value = userprofile.main_character

    return return_value


def get_user_for_character(character: EveCharacter) -> User:
    """
    Get the user for a character
    :param character:
    :return:
    """

    try:
        userprofile = character.character_ownership.user.profile
    except (
        EveCharacter.character_ownership.RelatedObjectDoesNotExist,
        CharacterOwnership.user.RelatedObjectDoesNotExist,
    ):
        return_value = get_sentinel_user()
    else:
        return_value = userprofile.user

    return return_value


def get_main_character_from_user(user: User) -> str:
    """
    Get the main character from a user
    :param user:
    :type user:
    :return:
    :rtype:
    """

    if user is None:
        sentinel_user = get_sentinel_user()

        return sentinel_user.username

    try:
        return_value = user.profile.main_character.character_name
    except AttributeError:
        return str(user)

    return return_value
