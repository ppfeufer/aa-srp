"""
Eve images helper
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

    :param character:
    :type character:
    :param size:
    :type size:
    :param as_html:
    :type as_html:
    :return:
    :rtype:
    """

    portrait_url = character_portrait_url(
        character_id=character.character_id, size=size
    )

    if as_html:
        return (
            '<img class="aasrp-character-portrait rounded" '
            f'src="{portrait_url}" alt="{character.character_name}" loading="lazy">'
        )

    return portrait_url


def get_type_render_url_from_type_id(
    evetype_id: int, size: int = 32, evetype_name: str = None, as_html: bool = False
) -> str:
    """
    Get type render from evetype_id

    :param evetype_id:
    :type evetype_id:
    :param size:
    :type size:
    :param evetype_name:
    :type evetype_name:
    :param as_html:
    :type as_html:
    :return:
    :rtype:
    """

    render_url = type_render_url(type_id=evetype_id, size=size)

    if as_html:
        alt_tag = f' alt="{evetype_name}"' if evetype_name else ""

        return (
            '<img class="aasrp-evetype-icon rounded" '
            f'src="{render_url}"{alt_tag} loading="lazy">'
        )

    return render_url
