"""
Tests for aasrp.helper.character
"""

# Django
from django.contrib.auth.models import Group
from django.test import TestCase

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.testing import (
    add_character_to_user,
    create_eve_character,
    create_fake_user,
)

# AA SRP
from aasrp.helper.character import (
    get_formatted_character_name,
    get_main_for_character,
    get_user_for_character,
)
from aasrp.helper.eve_images import get_character_portrait_from_evecharacter
from aasrp.helper.icons import copy_to_clipboard_icon
from aasrp.models import get_sentinel_user


class TestSentinelUser(TestCase):
    """
    Test the sentinel user
    """

    def test_sentinel_user(self):
        """
        Test that we get 'deleted' as username for the sentinel user

        :return:
        :rtype:
        """

        sentinel_user = get_sentinel_user()

        self.assertEqual(first=sentinel_user.username, second="deleted")


class TestGetFormattedCharacterName(TestCase):
    """
    Tests for get_formatted_character_name
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()
        cls.group = Group.objects.create(name="Enterprise Crew")

        cls.user_main_character = create_fake_user(
            character_id=1001, character_name="William T. Riker"
        )

        cls.alt_character = create_eve_character(
            character_id=1002, character_name="Thomas Riker"
        )

        add_character_to_user(user=cls.user_main_character, character=cls.alt_character)

        cls.character_without_profile = create_eve_character(
            character_id=1003, character_name="Christopher Pike"
        )

    def test_should_return_formatted_character_name(self):
        """
        Test should return a formatted character name

        :return:
        :rtype:
        """

        html = get_formatted_character_name(character=self.alt_character)
        expected_html = (
            "<small class='text-muted'>"
            f"{self.alt_character.alliance_ticker} "
            f"[{self.alt_character.corporation_ticker}] "
            f"</small><br>{self.alt_character.character_name}"
        )

        self.assertEqual(first=html, second=expected_html)

    def test_should_return_formatted_character_name_with_copy_icon(self):
        """
        Test should return a formatted character name with copy icon

        :return:
        :rtype:
        """

        self.maxDiff = None

        html = get_formatted_character_name(
            character=self.alt_character, with_copy_icon=True
        )

        icon = copy_to_clipboard_icon(
            data=self.alt_character.character_name,
            title="Copy character name to clipboard",
        )

        copy_icon = f"<sup>{icon}</sup>"

        expected_html = (
            "<small class='text-muted'>"
            f"{self.alt_character.alliance_ticker} "
            f"[{self.alt_character.corporation_ticker}] "
            f"</small><br>{self.alt_character.character_name}{copy_icon}"
        )

        self.assertEqual(first=html, second=expected_html)

    def test_should_return_formatted_character_name_with_portrait(self):
        """
        Test should return a formatted character name with a portrait

        :return:
        :rtype:
        """

        html = get_formatted_character_name(
            character=self.alt_character, with_portrait=True, inline=False
        )

        formatted_character_name = get_formatted_character_name(
            character=self.alt_character
        )

        character_portrait_html = get_character_portrait_from_evecharacter(
            character=self.alt_character, size=32, as_html=True
        )

        expected_html = (
            f"{character_portrait_html}<br>"
            "<span class='aasrp-character-portrait-character-name d-inline-block align-middle'>"
            f"{formatted_character_name}"
            "</span>"
        )

        self.assertEqual(first=html, second=expected_html)

    def test_should_return_formatted_character_name_with_portrait_inline(self):
        """
        Test should return a formatted character name with a portrait (inline)

        :return:
        :rtype:
        """

        html = get_formatted_character_name(
            character=self.alt_character, with_portrait=True
        )

        formatted_character_name = get_formatted_character_name(
            character=self.alt_character
        )

        character_portrait_html = get_character_portrait_from_evecharacter(
            character=self.alt_character, size=32, as_html=True
        )

        expected_html = (
            f"{character_portrait_html}"
            "<span class='aasrp-character-portrait-character-name d-inline-block align-middle'>"
            f"{formatted_character_name}"
            "</span>"
        )

        self.assertEqual(first=html, second=expected_html)

    def test_should_return_unknown_character_name(self):
        """
        Test should return "Unknown Character" for a broken EveCharacter object,
        e.g., when the EveCharacter object is None

        :return:
        :rtype:
        """

        html = get_formatted_character_name(character=None)

        expected_html = (
            "<span class='aasrp-character-portrait-character-name d-inline-block align-middle'>"
            "Unknown character"
            "</span>"
        )

        self.assertEqual(first=html, second=expected_html)


class TestGetMainForCharacter(TestCase):
    """
    Testing for get_main_for_character
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()
        cls.group = Group.objects.create(name="Enterprise Crew")

        cls.user_main_character = create_fake_user(
            character_id=1001, character_name="William T. Riker"
        )

        cls.alt_character = create_eve_character(
            character_id=1002, character_name="Thomas Riker"
        )

        cls.alt_character_2 = create_eve_character(
            character_id=1004, character_name="Jean Luc Riker"
        )

        add_character_to_user(user=cls.user_main_character, character=cls.alt_character)
        add_character_to_user(
            user=cls.user_main_character, character=cls.alt_character_2
        )

        cls.character_without_profile = create_eve_character(
            character_id=1003, character_name="Christopher Pike"
        )

    def test_get_main_for_character_returns_none(self):
        """
        Test if we get `None` as the main character

        :return:
        :rtype:
        """

        main_character = get_main_for_character(
            character=self.character_without_profile
        )

        self.assertIsNone(obj=main_character)

    def test_get_main_for_character_raises_exception_related_object_does_not_exist(
        self,
    ):
        """
        Test if we get `EveCharacter.userprofile.RelatedObjectDoesNotExist` as exception

        :return:
        :rtype:
        """

        get_main_for_character(character=self.character_without_profile)

        self.assertRaises(
            expected_exception=EveCharacter.userprofile.RelatedObjectDoesNotExist
        )

    def test_get_main_for_character_raises_exception_related_object_does_not_exist_2(
        self,
    ):
        """
        Test if we get `CharacterOwnership.user.RelatedObjectDoesNotExist` as exception

        :return:
        :rtype:
        """

        self.alt_character_2.character_ownership.user = None

        get_main_for_character(character=self.alt_character_2)

        self.assertRaises(
            expected_exception=CharacterOwnership.user.RelatedObjectDoesNotExist
        )

    def test_get_main_for_character_returns_main_character(self):
        """
        Test if we get the main character

        :return:
        :rtype:
        """

        main_character = get_main_for_character(character=self.alt_character)

        self.assertEqual(
            first=main_character.character_name,
            second=self.user_main_character.profile.main_character.character_name,
        )


class TestGetUserForCharacter(TestCase):
    """
    Tests for get_user_for_character
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()
        cls.group = Group.objects.create(name="Enterprise Crew")

        cls.user_main_character = create_fake_user(
            character_id=1001, character_name="William T. Riker"
        )

        cls.alt_character = create_eve_character(
            character_id=1002, character_name="Thomas Riker"
        )

        cls.alt_character_2 = create_eve_character(
            character_id=1004, character_name="Jean Luc Riker"
        )

        add_character_to_user(user=cls.user_main_character, character=cls.alt_character)
        add_character_to_user(
            user=cls.user_main_character, character=cls.alt_character_2
        )

        cls.character_without_profile = create_eve_character(
            character_id=1003, character_name="Christopher Pike"
        )

    def test_get_user_for_character_returns_sentinel_user(self):
        """
        Test if we get the sentinel user

        :return:
        :rtype:
        """

        returned_user = get_user_for_character(character=self.character_without_profile)
        sentinel_user = get_sentinel_user()

        self.assertEqual(first=returned_user, second=sentinel_user)

    def test_get_user_for_character_raises_exception_related_object_does_not_exist(
        self,
    ):
        """
        Test if we get `EveCharacter.userprofile.RelatedObjectDoesNotExist` as exception

        :return:
        :rtype:
        """

        get_user_for_character(character=self.character_without_profile)

        self.assertRaises(
            expected_exception=EveCharacter.userprofile.RelatedObjectDoesNotExist
        )

    def test_get_user_for_character_returns_user(self):
        """
        Test if we get a `User` object

        :return:
        :rtype:
        """

        returned_user = get_user_for_character(character=self.alt_character)

        self.assertEqual(
            first=returned_user, second=self.user_main_character.profile.user
        )

    def test_get_user_for_character_returns_sentinel_user_for_none(self):
        """
        Test if we get the sentinel user when user profile is None

        :return:
        :rtype:
        """

        self.alt_character_2.character_ownership.user = None

        returned_user = get_user_for_character(character=self.alt_character_2)
        expected_user = get_sentinel_user()

        self.assertEqual(first=returned_user, second=expected_user)
        self.assertRaises(
            expected_exception=CharacterOwnership.user.RelatedObjectDoesNotExist
        )
