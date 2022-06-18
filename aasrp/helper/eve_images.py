"""
Eve images
"""

# Alliance Auth
from allianceauth.eveonline.evelinks.eveimageserver import (
    character_portrait_url,
    type_render_url,
)
from allianceauth.eveonline.models import EveCharacter


def get_character_portrait_from_evecharacter(
    character: EveCharacter, size: int = 32, as_html: bool = False
) -> str:
    """
    Get the character portrait from EveCharacter model
    :param size:
    :param character:
    :param size:
    :param as_html:
    :return:
    """

    portrait_url = character_portrait_url(
        character_id=character.character_id, size=size
    )
    character_name = character.character_name

    return_value = portrait_url

    if as_html is True:
        return_value = (
            '<img class="aasrp-character-portrait img-rounded" '
            f'src="{portrait_url}" alt="{character_name}">'
        )

    return return_value


def get_type_render_url_from_type_id(
    evetype_id: int, size: int = 32, evetype_name: str = None, as_html: bool = False
) -> str:
    """
    Get type render from evetype_id
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
            alt_tag = f' alt="{evetype_name}"'

        return_value = (
            f'<img class="aasrp-evetype-icon img-rounded" src="{render_url}"{alt_tag}>'
        )

    return return_value
