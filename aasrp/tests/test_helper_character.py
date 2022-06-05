"""
Tests for aasrp.helper.character
"""

# Django
from django.contrib.auth.models import Group
from django.test import TestCase

# Alliance Auth
from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils

# Alliance Auth (External Libs)
from app_utils.testing import (
    add_character_to_user,
    create_eve_character,
    create_fake_user,
)

# AA SRP
from aasrp.helper.character import (
    get_main_character_from_user,
    get_main_for_character,
    get_user_for_character,
)
from aasrp.models import get_sentinel_user


class TestSentinelUser(TestCase):
    """
    Test the sentinel user
    """

    def test_sentinel_user(self):
        """
        Test that we get 'deleted' as username for the sentinel user
        :return:
        """

        sentinel_user = get_sentinel_user()

        self.assertEqual(sentinel_user.username, "deleted")


class TestGetMainForCharacter(TestCase):
    """
    Testing get_main_for_character
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

        add_character_to_user(cls.user_main_character, cls.alt_character)
        add_character_to_user(cls.user_main_character, cls.alt_character_2)

        cls.character_without_profile = create_eve_character(
            character_id=1003, character_name="Christopher Pike"
        )

    def test_get_main_for_character_returns_none(self):
        """
        Test if we get `None` as main character
        :return:
        """

        main_character = get_main_for_character(self.character_without_profile)

        self.assertIsNone(main_character)

    def test_get_main_for_character_raises_exception_related_object_does_not_exist(
        self,
    ):
        """
        Test if we get `EveCharacter.userprofile.RelatedObjectDoesNotExist` as exception
        :return:
        """

        get_main_for_character(self.character_without_profile)

        self.assertRaises(EveCharacter.userprofile.RelatedObjectDoesNotExist)

    def test_get_main_for_character_raises_exception_related_object_does_not_exist_2(
        self,
    ):
        """
        Test if we get `CharacterOwnership.user.RelatedObjectDoesNotExist` as exception
        :return:
        """

        self.alt_character_2.character_ownership.user = None

        get_main_for_character(self.alt_character_2)

        self.assertRaises(CharacterOwnership.user.RelatedObjectDoesNotExist)

    def test_get_main_for_character_returns_main_character(self):
        """
        Test if we get the main character
        :return:
        """

        main_character = get_main_for_character(self.alt_character)

        self.assertEqual(
            main_character.character_name,
            self.user_main_character.profile.main_character.character_name,
        )


class TestGetUserForCharacter(TestCase):
    """
    Test get_user_for_character
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

        add_character_to_user(cls.user_main_character, cls.alt_character)
        add_character_to_user(cls.user_main_character, cls.alt_character_2)

        cls.character_without_profile = create_eve_character(
            character_id=1003, character_name="Christopher Pike"
        )

    def test_get_user_for_character_returns_sentinel_user(self):
        """
        Test if we get the sentinel user
        :return:
        """

        returned_user = get_user_for_character(self.character_without_profile)
        sentinel_user = get_sentinel_user()

        self.assertEqual(returned_user, sentinel_user)

    def test_get_user_for_character_raises_exception_related_object_does_not_exist(
        self,
    ):
        """
        Test if we get `EveCharacter.userprofile.RelatedObjectDoesNotExist` as exception
        :return:
        """

        get_user_for_character(self.character_without_profile)

        self.assertRaises(EveCharacter.userprofile.RelatedObjectDoesNotExist)

    def test_get_user_for_character_returns_user(self):
        """
        Test if we get `User` object
        :return:
        """

        returned_user = get_user_for_character(self.alt_character)

        self.assertEqual(returned_user, self.user_main_character.profile.user)

    def test_get_user_for_character_returns_sentinel_user_for_none(self):
        """
        Test if we get the sentinel user when user profile is None
        :return:
        """

        self.alt_character_2.character_ownership.user = None

        returned_user = get_user_for_character(self.alt_character_2)
        expected_user = get_sentinel_user()

        self.assertEqual(returned_user, expected_user)
        self.assertRaises(CharacterOwnership.user.RelatedObjectDoesNotExist)


class TestGetMainCharacterFromUser(TestCase):
    """
    Test get_main_character_from_user
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

        cls.character_without_profile = create_eve_character(
            character_id=1003, character_name="Christopher Pike"
        )

    def test_get_main_character_from_user_should_return_character_name(self):
        """
        Test should return the main character name for a regular user
        :return:
        """

        character_name = get_main_character_from_user(self.user_main_character)

        self.assertEqual(character_name, "William T. Riker")

    def test_get_main_character_from_user_should_return_user_name(self):
        """
        Test should return just the user name for a user without a character
        :return:
        """

        user = AuthUtils.create_user("John Doe")

        character_name = get_main_character_from_user(user)

        self.assertEqual(character_name, "John Doe")

    def test_get_main_character_from_user_should_return_sentinel_user(self):
        """
        Test should return "deleted" as username (Sentinel User)
        :return:
        """

        user = get_sentinel_user()

        character_name = get_main_character_from_user(user)

        self.assertEqual(character_name, "deleted")

    def test_get_main_character_from_user_should_return_sentinel_user_for_none(self):
        """
        Test shouod return "deleted" (Sentinel User) if user is None
        :return:
        """

        user = None

        character_name = get_main_character_from_user(user)

        self.assertEqual(character_name, "deleted")
