# coding=utf-8

"""
eve images
"""

from allianceauth.eveonline.evelinks.eveimageserver import (
    character_portrait_url,
    type_render_url,
)
from allianceauth.eveonline.models import EveCharacter


def get_character_portrait_from_evecharacter(
    character: EveCharacter, size: int = 32, as_html: bool = False
) -> str:
    """
    get the character portrait from EveCharacter model
    :param size:
    :param character:
    :param portrait_size:
    :param as_html:
    :return:
    """
    portrait_url = character_portrait_url(
        character_id=character.character_id, size=size
    )

    return_value = portrait_url

    if as_html is True:
        return_value = (
            '<img class="aasrp-character-portrait img-rounded" '
            'src="{portrait_url}" alt="{character_name}">'.format(
                portrait_url=portrait_url, character_name=character.character_name
            )
        )

    return return_value


def get_type_render_url_from_type_id(
    evetype_id: int, size: int = 32, evetype_name: str = None, as_html: bool = False
) -> str:
    """
    get type render from evetype_id
    :param evetype_id:
    :param size:
    :param evetype_name:
    :param as_html:
    :return:
    """
    render_url = type_render_url(type_id=evetype_id, size=size)

    return_value = render_url

    if as_html is True:
        alt_tag = ""
        if evetype_name is not None:
            alt_tag = ' alt="{evetype_name}"'.format(evetype_name=evetype_name)

        return_value = (
            '<img class="aasrp-evetype-icon img-rounded" '
            'src="{render_url}"{alt_tag}>'.format(
                render_url=render_url, alt_tag=alt_tag
            )
        )

    return return_value
