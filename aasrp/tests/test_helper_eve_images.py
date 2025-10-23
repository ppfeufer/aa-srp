# Alliance Auth
from allianceauth.eveonline.evelinks import eveimageserver
from allianceauth.eveonline.models import EveCharacter

# AA SRP
from aasrp.helper.eve_images import (
    get_character_portrait_from_evecharacter,
    get_type_render_url_from_type_id,
)
from aasrp.tests import BaseTestCase


class TestGetTypeRenderUrlFromTypeId(BaseTestCase):
    """
    Test the get_type_render_url_from_type_id function.
    """

    def test_type_render_url_as_html_with_name(self):
        """
        Test the get_type_render_url_from_type_id function with HTML output and name.

        :return:
        :rtype:
        """

        evetype_id = 123
        size = 64
        evetype_name = "Test Type"
        result = get_type_render_url_from_type_id(
            evetype_id, size, evetype_name, as_html=True
        )
        self.assertIn('<img class="aasrp-evetype-icon rounded"', result)
        self.assertIn(
            f'src="{eveimageserver.type_render_url(type_id=evetype_id, size=size)}"',
            result,
        )
        self.assertIn(f'alt="{evetype_name}"', result)
        self.assertIn('loading="lazy"', result)

    def test_type_render_url_as_html_without_name(self):
        """
        Test the get_type_render_url_from_type_id function with HTML output without name.

        :return:
        :rtype:
        """

        evetype_id = 123
        size = 64
        result = get_type_render_url_from_type_id(evetype_id, size, as_html=True)

        self.assertIn('<img class="aasrp-evetype-icon rounded"', result)
        self.assertIn(
            f'src="{eveimageserver.type_render_url(type_id=evetype_id, size=size)}"',
            result,
        )
        self.assertIn('alt=""', result)
        self.assertIn('loading="lazy"', result)

    def test_type_render_url_as_plain_url(self):
        """
        Test the get_type_render_url_from_type_id function with plain URL output.

        :return:
        :rtype:
        """

        evetype_id = 123
        size = 64
        result = get_type_render_url_from_type_id(evetype_id, size, as_html=False)

        self.assertEqual(
            result, eveimageserver.type_render_url(type_id=evetype_id, size=size)
        )

    def test_type_render_url_with_default_size(self):
        """
        Test the get_type_render_url_from_type_id function with default size.

        :return:
        :rtype:
        """

        evetype_id = 123
        result = get_type_render_url_from_type_id(evetype_id)

        self.assertEqual(
            result, eveimageserver.type_render_url(type_id=evetype_id, size=32)
        )


class TestGetCharacterPortraitFromEvecharacter(BaseTestCase):
    """
    Test the get_character_portrait_from_evecharacter function.
    """

    def test_character_portrait_as_html_with_name(self):
        """
        Test the get_character_portrait_from_evecharacter function with HTML output and name.

        :return:
        :rtype:
        """

        character = EveCharacter.objects.create(
            character_id=12345,
            character_name="Test Character",
            corporation_id=2001,
            corporation_name="Test Corp",
        )
        result = get_character_portrait_from_evecharacter(
            character, size=64, as_html=True
        )

        self.assertIn('<img class="aasrp-character-portrait rounded"', result)
        self.assertIn(
            f'src="{eveimageserver.character_portrait_url(character_id=12345, size=64)}"',
            result,
        )
        self.assertIn('alt="Test Character"', result)
        self.assertIn('loading="lazy"', result)

    def test_character_portrait_as_plain_url(self):
        """
        Test the get_character_portrait_from_evecharacter function with plain URL output.

        :return:
        :rtype:
        """

        character = EveCharacter.objects.create(
            character_id=12345,
            character_name="Test Character",
            corporation_id=2001,
            corporation_name="Test Corp",
        )
        result = get_character_portrait_from_evecharacter(
            character, size=64, as_html=False
        )

        self.assertEqual(
            result, eveimageserver.character_portrait_url(character_id=12345, size=64)
        )

    def test_character_portrait_with_default_size(self):
        """
        Test the get_character_portrait_from_evecharacter function with default size.

        :return:
        :rtype:
        """

        character = EveCharacter.objects.create(
            character_id=12345,
            character_name="Test Character",
            corporation_id=2001,
            corporation_name="Test Corp",
        )
        result = get_character_portrait_from_evecharacter(character)

        self.assertEqual(
            result, eveimageserver.character_portrait_url(character_id=12345, size=32)
        )
