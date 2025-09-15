"""
Eve images helper

This module provides helper functions for working with Eve Online images.
It includes utilities for generating character portraits and type render URLs,
with options to return the results as plain URLs or HTML snippets.
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
    Retrieve the character portrait URL or HTML snippet from an EveCharacter object.

    This function generates the URL for a character's portrait based on the EveCharacter model.
    Optionally, it can return an HTML `<img>` tag for embedding the portrait in a webpage.

    :param character: The EveCharacter object containing the character's details.
    :type character: EveCharacter
    :param size: The size of the portrait image (default is 32).
    :type size: int
    :param as_html: Whether to return the portrait as an HTML `<img>` tag (default is False).
    :type as_html: bool
    :return: The portrait URL or an HTML `<img>` tag, depending on the `as_html` parameter.
    :rtype: str
    """

    # Generate the URL for the character's portrait using the character ID and specified size
    url = character_portrait_url(character_id=character.character_id, size=size)

    # Return an HTML `<img>` tag with the portrait URL if `as_html` is True,
    # otherwise return the plain portrait URL
    return (
        f'<img class="aasrp-character-portrait rounded" src="{url}" alt="{character.character_name}" loading="lazy">'
        if as_html
        else url
    )


def get_type_render_url_from_type_id(
    evetype_id: int, size: int = 32, evetype_name: str = None, as_html: bool = False
) -> str:
    """
    Retrieve the type render URL or HTML snippet for a given Eve type ID.

    This function generates the URL for a type render image based on the provided Eve type ID.
    Optionally, it can return an HTML `<img>` tag for embedding the image in a webpage.

    :param evetype_id: The ID of the Eve type for which the render is generated.
    :type evetype_id: int
    :param size: The size of the render image (default is 32).
    :type size: int
    :param evetype_name: The name of the Eve type, used as the `alt` attribute in the HTML tag (optional).
    :type evetype_name: str, optional
    :param as_html: Whether to return the render as an HTML `<img>` tag (default is False).
    :type as_html: bool
    :return: The render URL or an HTML `<img>` tag, depending on the `as_html` parameter.
    :rtype: str
    """

    # Generate the URL for the type render image using the provided Eve type ID and size
    url = type_render_url(type_id=evetype_id, size=size)

    # Return an HTML `<img>` tag with the render URL if `as_html` is True,
    # otherwise return the plain render URL
    return (
        f'<img class="aasrp-evetype-icon rounded" src="{url}" alt="{evetype_name or ""}" loading="lazy">'
        if as_html
        else url
    )
