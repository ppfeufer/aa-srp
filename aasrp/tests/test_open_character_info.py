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
from aasrp.models import SrpLink, SrpRequest
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
        settings = get_user_settings(user=user)
        settings.ui_character = character
        settings.save()

    def _url(self, srp_code=None, request_code=None):
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
        The main character has no UI scope, so only the UI character is returned.
        """

        characters = get_ui_characters_for_user(user=self.manager)

        self.assertQuerySetEqual(characters, [self.ui_character])

    def test_returns_token_for_ui_character(self):
        token = get_ui_token_for_user(user=self.manager, character=self.ui_character)

        self.assertIsNotNone(token)
        self.assertEqual(token.character_id, self.ui_character.character_id)

    def test_returns_no_token_without_character(self):
        self.assertIsNone(get_ui_token_for_user(user=self.manager, character=None))

    def test_returns_no_token_for_other_users_character(self):
        self.assertIsNone(
            get_ui_token_for_user(user=self.basic_user, character=self.ui_character)
        )


class TestUserSettingsFormUiCharacter(BaseOpenCharacterInfoTestCase):
    """
    Tests for the ui_character field of UserSettingsForm.
    """

    def test_field_removed_without_user(self):
        self.assertNotIn("ui_character", UserSettingsForm().fields)

    def test_field_removed_for_basic_user(self):
        form = UserSettingsForm(user=self.basic_user)

        self.assertNotIn("ui_character", form.fields)

    def test_field_limited_to_ui_characters_for_manager(self):
        form = UserSettingsForm(user=self.manager)

        self.assertQuerySetEqual(
            form.fields["ui_character"].queryset, [self.ui_character]
        )

    def test_rejects_character_without_ui_scope(self):
        main_character = self.manager.profile.main_character
        form = UserSettingsForm(
            data={"ui_character": main_character.pk},
            instance=get_user_settings(user=self.manager),
            user=self.manager,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("ui_character", form.errors)

    def test_saves_ui_character(self):
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
        self.client.force_login(self.manager)

        response = self.client.get(reverse("aasrp:user_settings"))

        self.assertContains(response, reverse("aasrp:add_ui_character"))
        self.assertContains(response, 'name="ui_character"')

    def test_basic_user_does_not_see_ui_character(self):
        self.client.force_login(self.basic_user)

        response = self.client.get(reverse("aasrp:user_settings"))

        self.assertNotContains(response, reverse("aasrp:add_ui_character"))
        self.assertNotContains(response, 'name="ui_character"')

    def test_basic_user_cannot_set_ui_character_via_post(self):
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
        request = RequestFactory().get(reverse("aasrp:add_ui_character"))
        request.user = user
        SessionMiddleware(lambda r: None).process_request(request)
        request._messages = FallbackStorage(request)

        # Skip the permission and token_required decorators
        view = general.add_ui_character.__wrapped__.__wrapped__

        return view(request, token)

    def test_sets_owned_character(self):
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
        stranger = create_eve_character(character_id=random_id(), character_name="Q")
        token = MagicMock(
            character_id=stranger.character_id, character_name=stranger.character_name
        )

        response = self._call(self.manager, token)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIsNone(get_user_settings(user=self.manager).ui_character)

    def test_redirects_basic_user(self):
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
        return self.client.post(
            url or self._url(), data="{}", content_type="application/json"
        )

    def _assert_json(self, response, status, success):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content)
        self.assertEqual(data["success"], success)

        return data

    def test_anonymous_is_redirected_by_alliance_auth(self):
        """
        Alliance Auth wraps all app URLs in main_character_required, so logged-out
        users are redirected before reaching the view. The JS treats the non-JSON
        response as an expired session.
        """

        response = self._post()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn("login", response.url)

    def test_basic_user_gets_json_403(self):
        self.client.force_login(self.basic_user)

        self._assert_json(self._post(), HTTPStatus.FORBIDDEN, False)

    def test_get_not_allowed(self):
        self.client.force_login(self.manager)

        self._assert_json(
            self.client.get(self._url()), HTTPStatus.METHOD_NOT_ALLOWED, False
        )

    def test_unknown_request_returns_404(self):
        self.client.force_login(self.manager)

        self._assert_json(
            self._post(self._url(request_code="doesnotexist")),
            HTTPStatus.NOT_FOUND,
            False,
        )

    def test_error_without_ui_character(self):
        self.client.force_login(self.manager)

        data = self._assert_json(self._post(), HTTPStatus.OK, False)

        self.assertIn("settings", str(data["message"]))

    @patch(ESI_PATH)
    def test_error_without_valid_token(self, mock_esi):
        self._set_ui_character(self.manager, self.ui_character)
        self.manager.token_set.filter(
            character_id=self.ui_character.character_id
        ).delete()
        self.client.force_login(self.manager)

        self._assert_json(self._post(), HTTPStatus.OK, False)
        mock_esi.client.User_Interface.PostUiOpenwindowInformation.assert_not_called()

    @patch(ESI_PATH)
    def test_error_when_request_has_no_character(self, mock_esi):
        self._set_ui_character(self.manager, self.ui_character)
        SrpRequest.objects.filter(pk=self.srp_request.pk).update(character=None)
        self.client.force_login(self.manager)

        self._assert_json(self._post(), HTTPStatus.OK, False)
        mock_esi.client.User_Interface.PostUiOpenwindowInformation.assert_not_called()

    @patch(ESI_PATH)
    def test_error_when_esi_fails(self, mock_esi):
        self._set_ui_character(self.manager, self.ui_character)
        mock_esi.client.User_Interface.PostUiOpenwindowInformation.return_value.result.side_effect = Exception(
            "boom"
        )
        self.client.force_login(self.manager)

        self._assert_json(self._post(), HTTPStatus.OK, False)

    @patch(ESI_PATH)
    def test_opens_window_for_request_character(self, mock_esi):
        self._set_ui_character(self.manager, self.ui_character)
        self.client.force_login(self.manager)

        self._assert_json(self._post(), HTTPStatus.OK, True)

        operation = mock_esi.client.User_Interface.PostUiOpenwindowInformation
        operation.assert_called_once()
        kwargs = operation.call_args.kwargs
        self.assertEqual(kwargs["target_id"], self.lost_character.character_id)
        self.assertEqual(kwargs["token"].character_id, self.ui_character.character_id)
        operation.return_value.result.assert_called_once_with(
            use_etag=False, use_cache=False, store_cache=False
        )


class TestOpenCharacterInfoButton(BaseOpenCharacterInfoTestCase):
    """
    Tests for the action button.
    """

    def _icons(self, show):
        request = RequestFactory().get("/")
        request.user = self.manager

        return get_srp_request_action_icons(
            request=request,
            srp_link=self.srp_link,
            srp_request=self.srp_request,
            show_open_character_info=show,
        )

    def test_button_hidden_by_default(self):
        self.assertNotIn("srp-request-open-info", self._icons(show=False))

    def test_button_does_not_navigate(self):
        html = self._icons(show=True)
        match = re.search(r"<button[^>]*srp-request-open-info[^>]*>", html)

        self.assertIsNotNone(match)
        button = match.group(0)
        self.assertIn('type="button"', button)
        self.assertIn(f'data-link="{self._url()}"', button)
        self.assertNotIn("href=", button)
        self.assertNotIn("data-bs-toggle", button)

    def test_button_hidden_when_request_has_no_character(self):
        self.srp_request.character = None

        self.assertNotIn("srp-request-open-info", self._icons(show=True))

    def test_requests_data_includes_button_only_with_ui_character(self):
        self.client.force_login(self.manager)
        url = reverse(
            "aasrp:ajax_srp_link_view_requests_data", args=[self.srp_link.srp_code]
        )

        response = self.client.get(url)
        self.assertNotIn("srp-request-open-info", response.json()[0]["actions"])

        self._set_ui_character(self.manager, self.ui_character)

        response = self.client.get(url)
        self.assertIn("srp-request-open-info", response.json()[0]["actions"])
