"""
Tests for the "show info in game & copy ISK amount" feature.

Covers the UI character helpers, the user settings form and views,
the AJAX endpoint and the action button.
"""

# Standard Library
import json
import re
from http import HTTPStatus
from unittest.mock import MagicMock, patch

# Third Party
from eve_sde.models import ItemType

# Django
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

# AA SRP
from aasrp.constants import ESI_SCOPE_UI_OPEN_WINDOW
from aasrp.form import UserSettingsForm
from aasrp.helper.icons import get_srp_request_action_icons
from aasrp.helper.user import (
    get_ui_characters_for_user,
    get_ui_token_for_user,
    get_user_settings,
)
from aasrp.models import Setting, SrpLink, SrpRequest
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import (
    add_character_to_user,
    create_eve_character,
    create_fake_user,
    random_id,
)
from aasrp.views import general

ESI_PATH = "aasrp.views.ajax.esi"


class BaseOpenCharacterInfoTestCase(BaseTestCase):
    """
    Base test case with a manager, a basic user, an SRP link and a request.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up a manager user, a basic user, an SRP link and an SRP request for testing.

        :return:
        """

        super().setUpClass()

        cls.manager = create_fake_user(
            character_id=random_id(),
            character_name="Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp_requests"],
        )
        cls.basic_user = create_fake_user(
            character_id=random_id(),
            character_name="Wesley Crusher",
            permissions=["aasrp.basic_access"],
        )

        # A second character of the manager, holding the UI scope
        cls.ui_character = create_eve_character(
            character_id=random_id(), character_name="William Riker"
        )
        add_character_to_user(
            user=cls.manager,
            character=cls.ui_character,
            scopes=[ESI_SCOPE_UI_OPEN_WINDOW],
        )

        cls.srp_link = SrpLink.objects.create(
            srp_name="Active SRP",
            srp_status=SrpLink.Status.ACTIVE,
            creator=cls.manager,
            fleet_time=timezone.now(),
            srp_code=get_random_string(length=16),
        )

        cls.lost_character = cls.basic_user.profile.main_character
        cls.srp_request = SrpRequest.objects.create(
            srp_link=cls.srp_link,
            creator=cls.basic_user,
            character=cls.lost_character,
            request_code=get_random_string(length=16),
            request_status=SrpRequest.Status.PENDING,
            loss_amount=100,
            payout_amount=125000000,
            ship=ItemType.objects.create(name="Test Ship", id=12345),
        )

    def _set_ui_character(self, user, character):
        """
        Set the UI character for a user in their settings.

        :param user:
        :param character:
        :return:
        """

        settings = get_user_settings(user=user)
        settings.ui_character = character
        settings.save()

    def _url(self, srp_code=None, request_code=None):
        """
        Generate the URL for the AJAX view to open character info in-game.

        :param srp_code:
        :param request_code:
        :return:
        """

        return reverse(
            "aasrp:ajax_srp_request_open_character_info",
            args=[
                srp_code or self.srp_link.srp_code,
                request_code or self.srp_request.request_code,
            ],
        )


class TestUiCharacterHelpers(BaseOpenCharacterInfoTestCase):
    """
    Tests for get_ui_characters_for_user and get_ui_token_for_user.
    """

    def test_only_returns_own_characters_with_ui_scope(self):
        """
        Test that get_ui_characters_for_user only returns characters owned by the user
        that have the ESI_SCOPE_UI_OPEN_WINDOW scope.

        :return:
        """

        characters = get_ui_characters_for_user(user=self.manager)

        self.assertQuerySetEqual(characters, [self.ui_character])

    def test_returns_token_for_ui_character(self):
        """
        Test that get_ui_token_for_user returns a token for the user's UI character.

        :return:
        """

        token = get_ui_token_for_user(user=self.manager, character=self.ui_character)

        self.assertIsNotNone(token)
        self.assertEqual(token.character_id, self.ui_character.character_id)

    def test_returns_no_token_without_character(self):
        """
        Test that get_ui_token_for_user returns None when no character is provided.

        :return:
        """

        self.assertIsNone(get_ui_token_for_user(user=self.manager, character=None))

    def test_returns_no_token_for_other_users_character(self):
        """
        Test that get_ui_token_for_user returns None when the character does not belong to the user.

        :return:
        """

        self.assertIsNone(
            get_ui_token_for_user(user=self.basic_user, character=self.ui_character)
        )


class TestUserSettingsFormUiCharacter(BaseOpenCharacterInfoTestCase):
    """
    Tests for the ui_character field of UserSettingsForm.
    """

    def test_field_removed_without_user(self):
        """
        Test that the ui_character field is removed from the form when no user is provided.

        :return:
        """

        self.assertNotIn("ui_character", UserSettingsForm().fields)

    def test_field_removed_for_basic_user(self):
        """
        Test that the ui_character field is removed from the form for a basic user.

        :return:
        """

        form = UserSettingsForm(user=self.basic_user)

        self.assertNotIn("ui_character", form.fields)

    def test_field_limited_to_ui_characters_for_manager(self):
        """
        Test that the ui_character field is limited to characters with the UI scope for a manager user.

        :return:
        """

        form = UserSettingsForm(user=self.manager)

        self.assertQuerySetEqual(
            form.fields["ui_character"].queryset, [self.ui_character]
        )

    def test_rejects_character_without_ui_scope(self):
        """
        Test that the form rejects a character that does not have the UI scope.

        :return:
        """

        main_character = self.manager.profile.main_character
        form = UserSettingsForm(
            data={"ui_character": main_character.pk},
            instance=get_user_settings(user=self.manager),
            user=self.manager,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("ui_character", form.errors)

    def test_saves_ui_character(self):
        """
        Test that the form saves the selected UI character to the user's settings.

        :return:
        """

        form = UserSettingsForm(
            data={"ui_character": self.ui_character.pk},
            instance=get_user_settings(user=self.manager),
            user=self.manager,
        )

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(
            get_user_settings(user=self.manager).ui_character, self.ui_character
        )


class TestUserSettingsViewUiCharacter(BaseOpenCharacterInfoTestCase):
    """
    Tests for the UI character section of the user settings view.
    """

    def test_manager_sees_add_character_button(self):
        """
        Test that a manager user sees the "Add UI Character" button in the user settings view.

        :return:
        """

        self.client.force_login(self.manager)

        response = self.client.get(reverse("aasrp:user_settings"))

        self.assertContains(response, reverse("aasrp:add_ui_character"))
        self.assertContains(response, 'name="ui_character"')

    def test_basic_user_does_not_see_ui_character(self):
        """
        Test that a basic user does not see the UI character section in the user settings view.

        :return:
        """

        self.client.force_login(self.basic_user)

        response = self.client.get(reverse("aasrp:user_settings"))

        self.assertNotContains(response, reverse("aasrp:add_ui_character"))
        self.assertNotContains(response, 'name="ui_character"')

    def test_basic_user_cannot_set_ui_character_via_post(self):
        """
        Test that a basic user cannot set the UI character via a POST request to the user settings view.

        :return:
        """

        self.client.force_login(self.basic_user)

        self.client.post(
            reverse("aasrp:user_settings"),
            data={"ui_character": self.ui_character.pk},
        )

        self.assertIsNone(get_user_settings(user=self.basic_user).ui_character)


class TestAddUiCharacterView(BaseOpenCharacterInfoTestCase):
    """
    Tests for the add_ui_character view, bypassing the EVE SSO decorator.
    """

    def _call(self, user, token):
        """
        Call the add_ui_character view with a mocked request and token.

        :param user:
        :param token:
        :return:
        """

        request = RequestFactory().get(reverse("aasrp:add_ui_character"))
        request.user = user
        SessionMiddleware(lambda r: None).process_request(request)
        request._messages = FallbackStorage(request)

        # Skip the permission and token_required decorators
        view = general.add_ui_character.__wrapped__.__wrapped__

        return view(request, token)

    def test_sets_owned_character(self):
        """
        Test that the add_ui_character view sets the UI character for a user when the character is owned by the user.

        :return:
        """

        token = MagicMock(
            character_id=self.ui_character.character_id,
            character_name=self.ui_character.character_name,
        )

        response = self._call(self.manager, token)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("aasrp:user_settings"))
        self.assertEqual(
            get_user_settings(user=self.manager).ui_character, self.ui_character
        )

    def test_rejects_character_not_owned_by_user(self):
        """
        Test that the add_ui_character view does not set the UI character for a user when the character is not owned by the user.

        :return:
        """

        stranger = create_eve_character(character_id=random_id(), character_name="Q")
        token = MagicMock(
            character_id=stranger.character_id, character_name=stranger.character_name
        )

        response = self._call(self.manager, token)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIsNone(get_user_settings(user=self.manager).ui_character)

    def test_redirects_basic_user(self):
        """
        Test that a basic user is redirected to the user settings view when trying to add a UI character.

        :return:
        """

        self.client.force_login(self.basic_user)

        response = self.client.get(reverse("aasrp:add_ui_character"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertNotIn("sso", response.url)


class TestOpenCharacterInfoView(BaseOpenCharacterInfoTestCase):
    """
    Tests for the srp_request_open_character_info AJAX view.

    Every response must be JSON and never a redirect, so the page never reloads.
    """

    def _post(self, url=None):
        """
        Helper method to send a POST request to the AJAX view.

        :param url:
        :return:
        """

        return self.client.post(
            url or self._url(), data="{}", content_type="application/json"
        )

    def _assert_json(self, response, status, success):
        """
        Helper method to assert that the response is JSON with the expected status and success value.

        :param response:
        :param status:
        :param success:
        :return:
        """

        self.assertEqual(response.status_code, status)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)

        self.assertEqual(data["success"], success)

        return data

    def test_anonymous_is_redirected_by_alliance_auth(self):
        """
        Test that an anonymous user is redirected to the login page by Alliance Auth when trying to access the AJAX view.

        :return:
        """

        response = self._post()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn("login", response.url)

    def test_basic_user_gets_json_403(self):
        """
        Test that a basic user gets a JSON 403 Forbidden response when trying to access the AJAX view.

        :return:
        """

        self.client.force_login(self.basic_user)

        self._assert_json(self._post(), HTTPStatus.FORBIDDEN, False)

    def test_get_not_allowed(self):
        """
        Test that a GET request to the AJAX view returns a 405 Method Not Allowed response.

        :return:
        """

        self.client.force_login(self.manager)

        self._assert_json(
            self.client.get(self._url()), HTTPStatus.METHOD_NOT_ALLOWED, False
        )

    def test_unknown_request_returns_404(self):
        """
        Test that a request with an unknown request code returns a 404 Not Found response.

        :return:
        """

        self.client.force_login(self.manager)

        self._assert_json(
            self._post(self._url(request_code="doesnotexist")),
            HTTPStatus.NOT_FOUND,
            False,
        )

    def test_error_without_ui_character(self):
        """
        Test that a manager without a UI character set in their settings gets an error message.

        :return:
        """

        self.client.force_login(self.manager)

        data = self._assert_json(self._post(), HTTPStatus.OK, False)

        self.assertIn("settings", str(data["message"]))

    @patch(ESI_PATH)
    def test_error_without_valid_token(self, mock_esi):
        """
        Test that a manager with a UI character but without a valid token gets an error message.

        :param mock_esi:
        :return:
        """

        self._set_ui_character(self.manager, self.ui_character)
        self.manager.token_set.filter(
            character_id=self.ui_character.character_id
        ).delete()
        self.client.force_login(self.manager)

        self._assert_json(self._post(), HTTPStatus.OK, False)
        mock_esi.client.User_Interface.PostUiOpenwindowInformation.assert_not_called()

    @patch(ESI_PATH)
    def test_error_when_request_has_no_character(self, mock_esi):
        """
        Test that a manager with a UI character and valid token gets an error message when the SRP request has no character.

        :param mock_esi:
        :return:
        """

        self._set_ui_character(self.manager, self.ui_character)

        SrpRequest.objects.filter(pk=self.srp_request.pk).update(character=None)

        self.client.force_login(self.manager)

        self._assert_json(self._post(), HTTPStatus.OK, False)
        mock_esi.client.User_Interface.PostUiOpenwindowInformation.assert_not_called()

    @patch(ESI_PATH)
    def test_error_when_esi_fails(self, mock_esi):
        """
        Test that a manager with a UI character and valid token gets an error message when the ESI call fails.

        :param mock_esi:
        :return:
        """

        self._set_ui_character(self.manager, self.ui_character)

        mock_esi.client.User_Interface.PostUiOpenwindowInformation.return_value.result.side_effect = Exception(
            "boom"
        )

        self.client.force_login(self.manager)

        self._assert_json(self._post(), HTTPStatus.OK, False)

    @patch(ESI_PATH)
    def test_opens_window_for_loser_character(self, mock_esi):
        """
        Test that a manager with a UI character and valid token opens the window for the character that lost the ship when the setting is set to LOSER.

        :param mock_esi:
        :return:
        """

        loss_character = create_eve_character(
            character_id=random_id(), character_name="Deanna Troi"
        )
        SrpRequest.objects.filter(pk=self.srp_request.pk).update(
            character=loss_character
        )
        self._set_ui_character(self.manager, self.ui_character)
        self.client.force_login(self.manager)

        with patch(
            "aasrp.views.ajax.Setting.objects.get_setting",
            return_value=Setting.PayoutReceiver.LOSER,
        ):
            data = self._assert_json(self._post(), HTTPStatus.OK, True)

        self.assertEqual(
            data["message"], "Information window for Deanna Troi opened in EVE"
        )
        operation = mock_esi.client.User_Interface.PostUiOpenwindowInformation
        operation.assert_called_once()
        kwargs = operation.call_args.kwargs
        self.assertEqual(kwargs["target_id"], loss_character.character_id)
        self.assertNotEqual(
            kwargs["target_id"], self.basic_user.profile.main_character.character_id
        )
        self.assertEqual(kwargs["token"].character_id, self.ui_character.character_id)
        operation.return_value.result.assert_called_once_with(
            use_etag=False, use_cache=False, store_cache=False
        )

    @patch(ESI_PATH)
    def test_opens_window_for_requestor_main_character(self, mock_esi):
        """
        Test that a manager with a UI character and valid token opens the window for the requestor's main character when the setting is set to REQUESTOR.

        :param mock_esi:
        :return:
        """

        loss_character = create_eve_character(
            character_id=random_id(), character_name="Deanna Troi"
        )
        SrpRequest.objects.filter(pk=self.srp_request.pk).update(
            character=loss_character
        )
        self._set_ui_character(self.manager, self.ui_character)
        self.client.force_login(self.manager)

        with patch(
            "aasrp.views.ajax.Setting.objects.get_setting",
            return_value=Setting.PayoutReceiver.REQUESTOR,
        ):
            data = self._assert_json(self._post(), HTTPStatus.OK, True)

        self.assertEqual(
            data["message"],
            (
                "Information window for "
                f"{self.basic_user.profile.main_character.character_name} opened in EVE"
            ),
        )
        operation = mock_esi.client.User_Interface.PostUiOpenwindowInformation
        operation.assert_called_once()
        kwargs = operation.call_args.kwargs
        self.assertEqual(
            kwargs["target_id"], self.basic_user.profile.main_character.character_id
        )
        self.assertNotEqual(kwargs["target_id"], loss_character.character_id)
        self.assertEqual(kwargs["token"].character_id, self.ui_character.character_id)
        operation.return_value.result.assert_called_once_with(
            use_etag=False, use_cache=False, store_cache=False
        )


class TestOpenCharacterInfoButton(BaseOpenCharacterInfoTestCase):
    """
    Tests for the action button.
    """

    def _icons(self, show):
        """
        Helper method to get the HTML for the action icons.

        :param show:
        :return:
        """

        self._set_ui_character(self.manager, self.ui_character if show else None)

        request = RequestFactory().get("/")
        request.user = self.manager

        return get_srp_request_action_icons(
            request=request,
            srp_link=self.srp_link,
            srp_request=self.srp_request,
        )

    def test_button_hidden_by_default(self):
        """
        Test that the action button is hidden by default (show=False).

        :return:
        """

        self.assertNotIn("srp-request-open-info", self._icons(show=False))

    def test_button_does_not_navigate(self):
        """
        Test that the action button does not navigate to a new page (no href, no data-bs-toggle).

        :return:
        """

        html = self._icons(show=True)
        match = re.search(r"<button[^>]*srp-request-open-info[^>]*>", html)

        self.assertIsNotNone(match)
        button = match.group(0)
        self.assertIn('type="button"', button)
        self.assertIn(f'data-link="{self._url()}"', button)
        self.assertNotIn("href=", button)
        self.assertNotIn("data-bs-toggle", button)

    def test_button_hidden_when_request_has_no_character(self):
        """
        Test that the action button is hidden when the SRP request has no character.

        :return:
        """

        self.srp_request.character = None

        self.assertNotIn("srp-request-open-info", self._icons(show=True))

    def test_requests_data_includes_button_only_with_ui_character(self):
        """
        Test that the AJAX endpoint for request data includes the action button only when the manager has a UI character set in their settings.

        :return:
        """

        self.client.force_login(self.manager)
        url = reverse(
            "aasrp:ajax_srp_link_view_requests_data", args=[self.srp_link.srp_code]
        )

        datatables_query = {
            "draw": 1,
            "start": 0,
            "length": 10,
            "search[value]": "",
            "search[regex]": "false",
            "columns[0][searchable]": "false",
        }

        response = self.client.get(url, datatables_query)
        self.assertNotIn("srp-request-open-info", response.json()["data"][0][8])

        self._set_ui_character(self.manager, self.ui_character)

        response = self.client.get(url, datatables_query)
        self.assertIn("srp-request-open-info", response.json()["data"][0][8])
