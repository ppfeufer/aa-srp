"""
Tests for the template tags
"""

# Django
from django.template import Context, Template
from django.test import TestCase

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA SRP
from aasrp.models import get_sentinel_user
from aasrp.tests.utils import create_fake_user


class TestMainCharacterName(TestCase):
    """
    Tests for main_character_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            template_string="{% load aasrp %}{{ user|main_character_name }}"
        )

    def test_should_contain_character_name_for_users_with_main(self):
        """
        Should contain the character name for a user with a main set

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(character_id=1001, character_name="Bruce Wayne")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="Bruce Wayne")

    def test_should_contain_user_character_name_for_users_without_main(self):
        """
        Should return the username for a users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user(username="john")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="john")

    def test_should_return_deleted_user_for_sentinel_user(self):
        """
        Should return "deleted" for the sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="deleted")

    def test_should_be_deleted_for_none(self):
        """
        Test should be empty

        :return:
        :rtype:
        """

        # given
        context = Context(dict_={"user": None})
        # when
        result = self.template.render(context=context)
        # then
        self.assertEqual(first=result, second="deleted")


class TestMainCharacterId(TestCase):
    """
    Tests for main_character_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.template = Template(
            template_string="{% load aasrp %}{{ user|main_character_id }}"
        )

    def test_should_contain_character_id_for_users_with_main(self):
        """
        Test should contain main character ID for users with main

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(character_id=1001, character_name="Bruce Wayne")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1001")

    def test_should_contain_dummy_id_for_users_without_main(self):
        """
        Test should contain a dummy ID (1) for users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user(username="john")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return a dummy ID (1) for the sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return a dummy ID (1) for None

        :return:
        :rtype:
        """

        # given
        context = Context(dict_={"user": None})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")


class TestMainCharacterCorporationName(TestCase):
    """
    Tests for main_character_corporation_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.template = Template(
            template_string="{% load aasrp %}{{ user|main_character_corporation_name }}"
        )

    def test_should_contain_corp_name_for_users_with_main(self):
        """
        Test should return the corporation name for users with a main character

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
        )
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="Wayne Tech Inc.")

    def test_should_be_empty_for_users_without_main(self):
        """
        Test should be empty for users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user(username="john")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_for_sentinel_user(self):
        """
        Test should be empty for the sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty for None

        :return:
        :rtype:
        """

        # given
        context = Context(dict_={"user": None})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="")


class TestMainCorporationId(TestCase):
    """
    Tests for main_character_corporation_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.template = Template(
            template_string="{% load aasrp %}{{ user|main_character_corporation_id }}"
        )

    def test_should_contain_corporation_id_for_users_with_main(self):
        """
        Test should return the main character's corp ID for users with a main character

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
        )
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="2001")

    def test_should_be_dummy_id_for_users_without_main(self):
        """
        Test should return a dummy ID (1) for users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user(username="john")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)
        # then

        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return a dummy ID (1) for the sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return a dummy ID (1) for None

        :return:
        :rtype:
        """

        # given
        context = Context(dict_={"user": None})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")


class TestMainCharacterAllianceName(TestCase):
    """
    Tests for main_character_alliance_name template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.template = Template(
            template_string="{% load aasrp %}{{ user|main_character_alliance_name }}"
        )

    def test_should_contain_alliance_name_for_users_with_main(self):
        """
        Test should return the main character's alliance name for users with a main character

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprices",
        )

        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="Wayne Enterprices")

    def test_should_be_empty_for_users_without_main(self):
        """
        Test should be empty for users without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user(username="john")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_when_main_is_not_in_an_alliance(self):
        """
        Test should be empty when a main character is not in an alliance

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=2012,
            character_name="William Riker",
            corporation_id=2012,
            corporation_name="Starfleet",
            corporation_ticker="SF",
            alliance_id=None,
        )

        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_for_sentinel_user(self):
        """
        Test should be empty for the sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="")

    def test_should_be_empty_for_none(self):
        """
        Test should be empty for None

        :return:
        :rtype:
        """

        # given
        context = Context(dict_={"user": None})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="")


class TestMainAllianceId(TestCase):
    """
    Tests for main_character_alliance_id template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.template = Template(
            template_string="{% load aasrp %}{{ user|main_character_alliance_id }}"
        )

    def test_should_contain_alliance_id_for_users_with_main(self):
        """
        Test should return the main character's alliance ID for user with a main character

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=1001,
            character_name="Bruce Wayne",
            corporation_id=2001,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=3001,
            alliance_name="Wayne Enterprises",
        )
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="3001")

    def test_should_be_dummy_id_for_users_without_main(self):
        """
        Test should return a dummy ID (1) for user without a main character

        :return:
        :rtype:
        """

        # given
        user = AuthUtils.create_user(username="john")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_dummy_id_when_main_is_not_in_an_alliance(self):
        """
        Test should return a dummy ID (1) when the main character is not in an alliance

        :return:
        :rtype:
        """

        # given
        user = create_fake_user(
            character_id=2012,
            character_name="William Riker",
            corporation_id=2012,
            corporation_name="Starfleet",
            corporation_ticker="SF",
            alliance_id=None,
        )

        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_sentinel_user(self):
        """
        Test should return a dummy ID (1) for the sentinel user

        :return:
        :rtype:
        """

        # given
        user = get_sentinel_user()
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")

    def test_should_be_dummy_id_for_none(self):
        """
        Test should return a dummy ID (1) for None

        :return:
        :rtype:
        """

        # given
        context = Context(dict_={"user": None})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second="1")
