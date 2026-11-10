"""
Tests for the template tags
"""

# Standard Library
from unittest.mock import MagicMock, patch

# Django
from django.template import Context, Template
from django.test import RequestFactory

# Alliance Auth
from allianceauth.tests.auth_utils import AuthUtils

# AA SRP
from aasrp.models import SrpLink, get_sentinel_user
from aasrp.templatetags.aasrp import srp_request_action_icons
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_fake_user, random_id


class TestMainCharacterName(BaseTestCase):
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
        user = create_fake_user(character_id=random_id(), character_name="Bruce Wayne")
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


class TestMainCharacterId(BaseTestCase):
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

        character_id = random_id()

        # given
        user = create_fake_user(character_id=character_id, character_name="Bruce Wayne")
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second=str(character_id))

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


class TestMainCharacterCorporationName(BaseTestCase):
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
            character_id=random_id(),
            character_name="Bruce Wayne",
            corporation_id=random_id(),
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


class TestMainCorporationId(BaseTestCase):
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

        corporation_id = random_id()

        # given
        user = create_fake_user(
            character_id=random_id(),
            character_name="Bruce Wayne",
            corporation_id=corporation_id,
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
        )
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second=str(corporation_id))

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


class TestMainCharacterAllianceName(BaseTestCase):
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
            character_id=random_id(),
            character_name="Bruce Wayne",
            corporation_id=random_id(),
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=random_id(),
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
            character_id=random_id(),
            character_name="William Riker",
            corporation_id=random_id(),
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


class TestMainAllianceId(BaseTestCase):
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

        alliance_id = random_id()

        # given
        user = create_fake_user(
            character_id=random_id(),
            character_name="Bruce Wayne",
            corporation_id=random_id(),
            corporation_name="Wayne Tech Inc.",
            corporation_ticker="WYT",
            alliance_id=alliance_id,
            alliance_name="Wayne Enterprises",
        )
        context = Context(dict_={"user": user})

        # when
        result = self.template.render(context=context)

        # then
        self.assertEqual(first=result, second=str(alliance_id))

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
            character_id=random_id(),
            character_name="William Riker",
            corporation_id=random_id(),
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


class TestSrpLinkActions(BaseTestCase):
    """
    Tests for srp_link_actions template tag
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the test class by initializing the template for srp_link_actions.

        :return:
        """

        super().setUpClass()

        cls.template = Template(
            template_string="{% load aasrp %}{{ srp_link|srp_link_actions:request }}"
        )

    def test_should_return_empty_string_when_srp_link_is_none(self):
        """
        Test that the template tag returns an empty string when srp_link is None.

        :return:
        """

        context = Context(
            dict_={"srp_link": None, "request": RequestFactory().get("/")}
        )

        result = self.template.render(context=context)

        self.assertEqual(first=result, second="")

    def test_should_render_raw_html_from_action_icons(self):
        """
        Test that the template tag renders raw HTML returned from dashboard_action_icons.

        :return:
        """

        srp_link = SrpLink(srp_name="SRP", fleet_time="2026-01-01T00:00:00Z")
        context = Context(
            dict_={"srp_link": srp_link, "request": RequestFactory().get("/")}
        )

        with patch("aasrp.templatetags.aasrp.dashboard_action_icons") as mock_icons:
            mock_icons.return_value = "<span>View & Edit</span>"

            result = self.template.render(context=context)

        self.assertEqual(first=result, second="<span>View & Edit</span>")

    def test_should_pass_request_and_srp_link_to_dashboard_action_icons(self):
        """
        Test that the template tag passes the request and srp_link to dashboard_action_icons.

        :return:
        """

        srp_link = SrpLink(srp_name="SRP", fleet_time="2026-01-01T00:00:00Z")
        request = RequestFactory().get("/")
        context = Context(dict_={"srp_link": srp_link, "request": request})

        with patch("aasrp.templatetags.aasrp.dashboard_action_icons") as mock_icons:
            mock_icons.return_value = "<span>Actions</span>"

            self.template.render(context=context)

        mock_icons.assert_called_once_with(request=request, srp_link=srp_link)


class TestSrpRequestActionIcons(BaseTestCase):
    """
    Tests for srp_request_action_icons template tag
    """

    def test_returns_empty_string_when_user_has_no_required_permissions(self):
        """
        Test that the template tag returns an empty string when the user has no required permissions.

        :return:
        """

        user = create_fake_user(
            character_id=random_id(),
            character_name="Miles O'Brien",
            permissions=["aasrp.basic_access"],
        )
        request = RequestFactory().get("/")
        request.user = user

        with patch(
            "aasrp.templatetags.aasrp.get_srp_request_action_icons"
        ) as mock_icons:
            result = srp_request_action_icons(
                context={"request": request},
                srp_link=MagicMock(),
                srp_request=MagicMock(),
            )

        self.assertEqual(first=result, second="")
        mock_icons.assert_not_called()

    def test_returns_icons_when_user_has_manage_srp_permission(self):
        """
        Test that the template tag returns the action icons when the user has the "aasrp.manage_srp" permission.

        :return:
        """

        user = create_fake_user(
            character_id=random_id(),
            character_name="Kira Nerys",
            permissions=["aasrp.manage_srp"],
        )
        request = RequestFactory().get("/")
        request.user = user
        srp_link = MagicMock()
        srp_request = MagicMock()

        with patch(
            "aasrp.templatetags.aasrp.get_srp_request_action_icons"
        ) as mock_icons:
            mock_icons.return_value = "<button>Open</button>"

            result = srp_request_action_icons(
                context={"request": request},
                srp_link=srp_link,
                srp_request=srp_request,
            )

        self.assertEqual(first=result, second="<button>Open</button>")
        mock_icons.assert_called_once_with(request, srp_link, srp_request)

    def test_returns_icons_when_user_has_manage_srp_requests_permission(self):
        """
        Test that the template tag returns the action icons when the user has the "aasrp.manage_srp_requests" permission.

        :return:
        """

        user = create_fake_user(
            character_id=random_id(),
            character_name="Jadzia Dax",
            permissions=["aasrp.manage_srp_requests"],
        )
        request = RequestFactory().get("/")
        request.user = user
        srp_link = MagicMock()
        srp_request = MagicMock()

        with patch(
            "aasrp.templatetags.aasrp.get_srp_request_action_icons"
        ) as mock_icons:
            mock_icons.return_value = "<span>Actions</span>"

            result = srp_request_action_icons(
                context={"request": request},
                srp_link=srp_link,
                srp_request=srp_request,
            )

        self.assertEqual(first=result, second="<span>Actions</span>")
        mock_icons.assert_called_once_with(request, srp_link, srp_request)

    def test_raises_key_error_when_request_is_missing_from_context(self):
        """
        Test that the template tag raises a KeyError when the 'request' key is missing from the context.

        :return:
        """

        with self.assertRaises(KeyError):
            srp_request_action_icons(
                context={},
                srp_link=MagicMock(),
                srp_request=MagicMock(),
            )


class TestFirstLineExcerpt(BaseTestCase):
    """
    Tests for first_line_excerpt template filter
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the test class by initializing the template for first_line_excerpt.

        :return:
        """

        super().setUpClass()

        cls.template = Template(
            template_string="{% load aasrp %}{{ text|first_line_excerpt }}"
        )

    def test_returns_first_line_for_multiline_text(self):
        """
        Test that the template filter returns the first line of a multiline text.

        :return:
        """

        context = Context(dict_={"text": "First line\nSecond line\nThird line"})

        result = self.template.render(context=context)

        self.assertEqual(first=result, second="First line")

    def test_ignores_leading_blank_lines_and_trims_surrounding_whitespace(self):
        """
        Test that the template filter ignores leading blank lines and trims surrounding whitespace.

        :return:
        """

        context = Context(dict_={"text": "\n\n   First line   \nSecond line"})

        result = self.template.render(context=context)

        self.assertEqual(first=result, second="First line")

    def test_returns_single_line_when_text_has_no_line_breaks(self):
        """
        Test that the template filter returns the single line when the text has no line breaks.

        :return:
        """

        context = Context(dict_={"text": "  Single line value  "})

        result = self.template.render(context=context)

        self.assertEqual(first=result, second="Single line value")

    def test_returns_empty_string_for_empty_or_whitespace_only_text(self):
        """
        Test that the template filter returns an empty string for empty or whitespace-only text.

        :return:
        """

        context = Context(dict_={"text": "   \n\n  "})

        result = self.template.render(context=context)

        self.assertEqual(first=result, second="")
