# coding=utf-8

"""
some helper functions
so we don't mess up other files too much
"""

from aasrp.helper.eve_images import get_character_portrait_from_evecharacter
from aasrp.models import get_sentinel_user

from django.contrib.auth.models import User

from allianceauth.eveonline.models import EveCharacter


def get_formatted_character_name(
    character: EveCharacter,
    with_portrait: bool = False,
    portrait_size: int = 32,
    inline: bool = True,
) -> str:
    """
    get character name with alliance and corp ticker
    :param inline:
    :param portrait_size:
    :param with_portrait:
    :param character:
    """

    character_name = character.character_name

    character__corporation_ticker = ""
    if character.corporation_ticker:
        character__corporation_ticker = "[{corporation_ticker}] ".format(
            corporation_ticker=character.corporation_ticker
        )

    character__alliance_ticker = ""
    if character.alliance_ticker:
        character__alliance_ticker = "{alliance_ticker} ".format(
            alliance_ticker=character.alliance_ticker
        )

    character_name_formatted = (
        "<small class='text-muted'>{alliance_ticker}{corporation_ticker}</small>"
        "<br>{character_name}".format(
            alliance_ticker=character__alliance_ticker,
            corporation_ticker=character__corporation_ticker,
            character_name=character_name,
        )
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
            "{character_portrait}{line_break}"
            "<span class='aasrp-character-portrait-character-name'>"
            "{character_name_formatted}"
            "</span>".format(
                character_portrait=character_portrait_html,
                line_break=line_break,
                character_name_formatted=character_name_formatted,
            )
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
