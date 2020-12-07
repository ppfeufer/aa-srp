# coding=utf-8

"""
some helper functions
so we don't mess up other files too much
"""

from django.contrib.auth.models import User

from allianceauth.eveonline.models import EveCharacter


def get_formatted_character_name(character: EveCharacter) -> str:
    """
    get character name with alliance and corp ticker
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
        "{alliance_ticker}{corporation_ticker}{character_name}".format(
            alliance_ticker=character__alliance_ticker,
            corporation_ticker=character__corporation_ticker,
            character_name=character_name,
        )
    )

    return character_name_formatted


def get_main_for_character(character: EveCharacter) -> EveCharacter:
    """
    get themain character for a given eve character
    :param character:
    """

    return character.userprofile.main_character


def get_user_for_character(character: EveCharacter) -> User:
    """
    get the user for a character
    :param character:
    :return:
    """

    return character.userprofile.user
