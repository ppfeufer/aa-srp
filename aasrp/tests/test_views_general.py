"""
Tests for the views in aasrp/views/general.py
"""

# Standard Library
from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

# Django
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

# Alliance Auth (External Libs)
from app_utils.testing import create_fake_user

# AA SRP
from aasrp.models import SrpLink, SrpRequest, UserSetting
from aasrp.tests import BaseTestCase
from aasrp.views.general import (
    _save_srp_request,
    complete_srp_link,
    delete_srp_link,
    disable_srp_link,
    enable_srp_link,
    request_srp,
    srp_link_view_requests,
)


class BaseViewsTestCase(BaseTestCase):
    """
    Base test case for views tests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up a SrpLink instance for testing.

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.user_jean_luc_picard = create_fake_user(
            character_id=1000,
            character_name="Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )
        cls.user_wesley_crusher = create_fake_user(
            character_id=1001,
            character_name="Wesley Crusher",
            permissions=["aasrp.basic_access"],
        )


class TestSrpLinkDelete(BaseViewsTestCase):
    """
    Test the srp_link_delete view.
    """

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_srp_link_deleted_successfully(self, mock_get_srp_link):
        """
        Test the srp_link_delete view for a user with the manage_srp permissions and successful deletion.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(srp_code="SRP123", fleet_time=datetime.now())
        mock_get_srp_link.return_value = srp_link

        factory = RequestFactory()
        request = factory.get(reverse("aasrp:delete_srp_link", args=["SRP123"]))
        request.user = user

        # Add session and messages middleware to the request
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = delete_srp_link(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_srp_link_not_found(self, mock_get_srp_link):
        """
        Test the srp_link_delete view for a user with the manage_srp permissions and not found.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        mock_get_srp_link.side_effect = SrpLink.DoesNotExist

        factory = RequestFactory()
        request = factory.get(reverse("aasrp:delete_srp_link", args=["SRP123"]))
        request.user = user

        # Add session and messages middleware to the request
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = delete_srp_link(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)


class TestSrpLinkDisable(BaseViewsTestCase):
    """
    Test the srp_link_disable view.
    """

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_disable_srp_link_successfully(self, mock_get_srp_link):
        """
        Test the srp_link_disable view for a user with the manage_srp permissions and successful disabling.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(srp_code="SRP123", fleet_time=datetime.now())
        mock_get_srp_link.return_value = srp_link

        factory = RequestFactory()
        request = factory.post(reverse("aasrp:disable_srp_link", args=["SRP123"]))
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = disable_srp_link(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_disable_srp_link_not_found(self, mock_get_srp_link):
        """
        Test the srp_link_disable view for a user with the manage_srp permissions and not found.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        mock_get_srp_link.side_effect = SrpLink.DoesNotExist

        factory = RequestFactory()
        request = factory.post(reverse("aasrp:disable_srp_link", args=["SRP123"]))
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = disable_srp_link(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)


class TestSrpLinkEnable(BaseViewsTestCase):
    """
    Test the srp_link_enable view.
    """

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_enable_srp_link_successfully(self, mock_get_srp_link):
        """
        Test the srp_link_enable view for a user with the manage_srp permissions and successful enabling.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_code="SRP123",
            srp_status=SrpLink.Status.CLOSED,
            fleet_time=datetime.now(),
        )
        mock_get_srp_link.return_value = srp_link

        factory = RequestFactory()
        request = factory.get(reverse("aasrp:enable_srp_link", args=["SRP123"]))
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = enable_srp_link(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)
        srp_link.refresh_from_db()
        self.assertEqual(srp_link.srp_status, SrpLink.Status.ACTIVE)

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_enable_srp_link_not_found(self, mock_get_srp_link):
        """
        Test the srp_link_enable view for a user with the manage_srp permissions and not found.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        mock_get_srp_link.side_effect = SrpLink.DoesNotExist

        factory = RequestFactory()
        request = factory.post(reverse("aasrp:enable_srp_link", args=["SRP123"]))
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = enable_srp_link(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)


class TestSrpLinkViewRequests(BaseViewsTestCase):
    """
    Test the srp_link_view_requests view.
    """

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_view_requests_srp_link_not_found(self, mock_get_srp_link):
        """
        Test the srp_link_view_requests view for a user with the manage_srp permissions and not found.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        mock_get_srp_link.side_effect = SrpLink.DoesNotExist

        factory = RequestFactory()
        request = factory.get(reverse("aasrp:view_srp_requests", args=["SRP123"]))
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = srp_link_view_requests(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)
        self.assertEqual(len(messages.get_messages(request)), 1)
        self.assertEqual(
            str(list(messages.get_messages(request))[0]),
            "Unable to locate SRP link with ID SRP123",
        )


class TestCompleteSrpLink(BaseViewsTestCase):
    """
    Test the complete_srp_link view.
    """

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_complete_srp_link_successfully(self, mock_get_srp_link):
        """
        Test the complete_srp_link view for a user with the manage_srp permissions and successful completion.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_code="SRP123",
            srp_status=SrpLink.Status.ACTIVE,
            fleet_time=datetime.now(),
        )
        mock_get_srp_link.return_value = srp_link

        factory = RequestFactory()
        request = factory.get(reverse("aasrp:complete_srp_link", args=["SRP123"]))
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = complete_srp_link(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)
        self.assertEqual(len(messages.get_messages(request)), 1)
        self.assertEqual(
            str(list(messages.get_messages(request))[0]), "SRP link marked as completed"
        )
        srp_link.refresh_from_db()
        self.assertEqual(srp_link.srp_status, SrpLink.Status.COMPLETED)

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_complete_srp_link_not_found(self, mock_get_srp_link):
        """
        Test the complete_srp_link view for a user with the manage_srp permissions and not found.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        mock_get_srp_link.side_effect = SrpLink.DoesNotExist

        factory = RequestFactory()
        request = factory.get(reverse("aasrp:complete_srp_link", args=["SRP123"]))
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = complete_srp_link(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)
        self.assertEqual(len(messages.get_messages(request)), 1)
        self.assertEqual(
            str(list(messages.get_messages(request))[0]),
            "Unable to locate SRP link with ID SRP123",
        )


class TestRequestSrp(BaseViewsTestCase):
    """
    Test the request_srp view.
    """

    def setUp(self):
        """
        Set up a SrpLink instance for testing.

        :return:
        :rtype:
        """

        self.user = self.user_wesley_crusher
        self.client.force_login(self.user)
        self.srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            fleet_time=timezone.now(),
            fleet_doctrine="Doctrine A",
            aar_link="http://example.com/aar",
            srp_code="SRP123",
            fleet_commander=self.user.profile.main_character,
            creator=self.user,
            srp_status=SrpLink.Status.ACTIVE,
        )
        self.url = reverse("aasrp:request_srp", args=[self.srp_link.srp_code])

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_request_srp_link_not_found(self, mock_get_srp_link):
        """
        Test the request_srp view for a user with the basic_access permissions and not found.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_wesley_crusher
        self.client.force_login(user)

        mock_get_srp_link.side_effect = SrpLink.DoesNotExist

        factory = RequestFactory()
        request = factory.post(
            reverse("aasrp:request_srp", args=["SRP123"]),
            {
                "killboard_link": "https://zkillboard.com/kill/12345/",
                "additional_info": "Test info",
            },
        )
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = request_srp(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)
        self.assertEqual(len(messages.get_messages(request)), 1)
        self.assertEqual(
            str(list(messages.get_messages(request))[0]),
            "Unable to locate SRP Fleet using SRP code SRP123",
        )

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_request_srp_link_not_active(self, mock_get_srp_link):
        """
        Test the request_srp view for a user with the basic_access permissions and not active.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        user = self.user_wesley_crusher
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_code="SRP123",
            srp_status=SrpLink.Status.CLOSED,
            fleet_time=datetime.now(),
        )
        mock_get_srp_link.return_value = srp_link

        factory = RequestFactory()
        request = factory.post(
            reverse("aasrp:request_srp", args=["SRP123"]),
            {
                "killboard_link": "https://zkillboard.com/kill/12345/",
                "additional_info": "Test info",
            },
        )
        request.user = user

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = request_srp(request, "SRP123")

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("aasrp:srp_links"), response.url)
        self.assertEqual(len(messages.get_messages(request)), 1)
        self.assertEqual(
            str(list(messages.get_messages(request))[0]),
            "This SRP link is no longer available for SRP requests.",
        )

    def test_renders_form_on_get_request(self):
        """
        Test that a GET request to the view shows the form.

        :return:
        :rtype:
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form")

    @patch("aasrp.models.SrpRequest.objects.get_kill_id")
    @patch("aasrp.models.SrpRequest.objects.get_kill_data")
    @patch("aasrp.views.general._save_srp_request")
    def test_creates_srp_request_on_valid_post(
        self, mock_save_request, mock_get_kill_data, mock_get_kill_id
    ):
        """
        Test that a valid form submission creates a new SrpRequest instance.

        :param mock_save_request:
        :type mock_save_request:
        :param mock_get_kill_data:
        :type mock_get_kill_data:
        :param mock_get_kill_id:
        :type mock_get_kill_id:
        :return:
        :rtype:
        """

        mock_get_kill_id.return_value = "kill_id_123"
        mock_get_kill_data.return_value = (
            1,
            "1000000",
            self.user.profile.main_character.character_id,
        )
        mock_save_request.return_value = SrpRequest(
            killboard_link="https://zkillboard.com/kill/123456789/",
            srp_link=self.srp_link,
            creator=self.user,
        )
        form_data = {
            "killboard_link": "https://zkillboard.com/kill/123456789/",
            "additional_info": "Test info",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, reverse("aasrp:srp_links"))

    @patch("aasrp.models.SrpRequest.objects.get_kill_id")
    @patch("aasrp.models.SrpRequest.objects.get_kill_data")
    def test_shows_error_for_invalid_killmail(
        self, mock_get_kill_data, mock_get_kill_id
    ):
        """
        Test that an invalid killmail shows an error message.

        :param mock_get_kill_data:
        :type mock_get_kill_data:
        :param mock_get_kill_id:
        :type mock_get_kill_id:
        :return:
        :rtype:
        """

        mock_get_kill_id.side_effect = ValueError("Invalid killmail")
        form_data = {
            "killboard_link": "https://zkillboard.com/kill/128743453/",
            "additional_info": "Test info",
        }
        response = self.client.post(self.url, data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Invalid killmail")

    @patch("aasrp.models.SrpRequest.objects.get_kill_id")
    @patch("aasrp.models.SrpRequest.objects.get_kill_data")
    def test_shows_error_when_character_not_owned(
        self, mock_get_kill_data, mock_get_kill_id
    ):
        """
        Test that a killmail not involving the user's character shows an error message.

        :param mock_get_kill_data:
        :type mock_get_kill_data:
        :param mock_get_kill_id:
        :type mock_get_kill_id:
        :return:
        :rtype:
        """

        mock_get_kill_id.return_value = "kill_id_123"
        mock_get_kill_data.return_value = (1, "1000000", 99999)
        form_data = {
            "killboard_link": "https://zkillboard.com/kill/128743453/",
            "additional_info": "Test info",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, reverse("aasrp:srp_links"))


class TestViewOwnRequests(BaseViewsTestCase):
    """
    Test the view_own_requests view.
    """

    def test_redirects_unauthenticated_user(self):
        """
        Test that an unauthenticated user is redirected to the login page when trying to access the view_own_requests view.

        :return:
        :rtype:
        """

        response = self.client.get(reverse("aasrp:own_srp_requests"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_renders_template_for_authenticated_user(self):
        """
        Test that an authenticated user can access the view_own_requests view and the correct template is used.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_jean_luc_picard)

        response = self.client.get(reverse("aasrp:own_srp_requests"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "aasrp/view-own-requests.html")


class TestUserSettingsView(BaseViewsTestCase):
    def test_renders_user_settings_template_for_authenticated_user(self):
        """
        Test that an authenticated user can access the user_settings view and the correct template is used.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_wesley_crusher)
        response = self.client.get(reverse("aasrp:user_settings"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "aasrp/user-settings.html")

    def test_redirects_unauthenticated_user_to_login(self):
        """
        Test that an unauthenticated user is redirected to the login page when trying to access the user_settings view.

        :return:
        :rtype:
        """

        response = self.client.get(reverse("aasrp:user_settings"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn("/login/", response.url)

    def test_saves_valid_user_settings_form(self):
        """
        Test that a valid user settings form is saved correctly.

        :return:
        :rtype:
        """

        user = self.user_wesley_crusher
        self.client.force_login(user)

        user_settings = UserSetting.objects.create(
            user=user, disable_notifications=False
        )
        form_data = {"disable_notifications": "on"}
        response = self.client.post(reverse("aasrp:user_settings"), data=form_data)
        user_settings.refresh_from_db()

        self.assertEqual(user_settings.disable_notifications, True)
        self.assertRedirects(response, reverse("aasrp:user_settings"))

    def test_does_not_save_invalid_user_settings_form(self):
        """
        Test that an invalid user settings form does not change the settings.

        :return:
        :rtype:
        """

        user = self.user_wesley_crusher
        self.client.force_login(user)

        user_settings = UserSetting.objects.create(
            user=user, disable_notifications=False
        )
        form_data = {}  # Checkbox omitted
        response = self.client.post(reverse("aasrp:user_settings"), data=form_data)
        user_settings.refresh_from_db()

        self.assertEqual(user_settings.disable_notifications, False)
        self.assertRedirects(response, reverse("aasrp:user_settings"))


class SrpLinkAddViewTests(BaseViewsTestCase):
    """
    Test the srp_link_add view.
    """

    def test_renders_add_srp_link_template_for_authenticated_user_with_permission(self):
        """
        Test that an authenticated user with the manage_srp permission can access the srp_link_add view and the correct template is used.

        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        response = self.client.get(reverse("aasrp:add_srp_link"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "aasrp/link-add.html")

    def test_redirects_unauthorized_user_to_login(self):
        """
        Test that an unauthorized user is redirected to the login page when trying to access the srp_link_add view.

        :return:
        :rtype:
        """

        user = self.user_wesley_crusher
        self.client.force_login(user)

        response = self.client.get(reverse("aasrp:add_srp_link"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn("/login/", response.url)

    def test_creates_srp_link_with_valid_form_data(self):
        """
        Test that a valid form submission creates a new SrpLink instance.

        :return:
        :rtype:
        """

        user = self.user_jean_luc_picard
        self.client.force_login(user)

        form_data = {
            "srp_name": "Test SRP",
            "fleet_type": "",
            "fleet_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fleet_doctrine": "Doctrine A",
            "aar_link": "http://example.com/aar",
        }
        response = self.client.post(reverse("aasrp:add_srp_link"), data=form_data)

        self.assertEqual(SrpLink.objects.count(), 1)

        srp_link = SrpLink.objects.first()

        self.assertEqual(srp_link.srp_name, "Test SRP")
        self.assertRedirects(response, reverse("aasrp:srp_links"))


class TestSrpLinkEditView(BaseViewsTestCase):
    """
    Test the srp_link_edit view.
    """

    def setUp(self):
        """
        Set up a SrpLink instance for testing.

        :return:
        :rtype:
        """

        self.user = self.user_jean_luc_picard
        self.client.force_login(self.user)
        self.srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            fleet_time=timezone.now(),
            fleet_doctrine="Doctrine A",
            aar_link="http://example.com/aar",
            srp_code="SRP123",
            fleet_commander=self.user.profile.main_character,
            creator=self.user,
        )
        self.url = reverse("aasrp:edit_srp_link", args=[self.srp_link.srp_code])

    def test_updates_aar_link_successfully(self):
        """
        Test that a valid form submission updates the aar_link of the SrpLink instance.

        :return:
        :rtype:
        """

        form_data = {"aar_link": "http://example.com/new-aar"}
        response = self.client.post(self.url, data=form_data)

        self.srp_link.refresh_from_db()
        self.assertEqual(self.srp_link.aar_link, "http://example.com/new-aar")
        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_shows_error_for_invalid_srp_code(self):
        """
        Test that accessing the view with an invalid srp_code redirects to the srp_links page.

        :return:
        :rtype:
        """

        invalid_url = reverse("aasrp:edit_srp_link", args=["INVALID_CODE"])
        response = self.client.get(invalid_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_shows_form_with_existing_data_on_get(self):
        """
        Test that a GET request to the view shows the form with existing data.

        :return:
        :rtype:
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.srp_link.aar_link)


class TestSaveSrpRequest(BaseTestCase):
    """
    Test the _save_srp_request function.
    """

    def setUp(self):
        """
        Set up common test data.

        :return:
        :rtype:
        """

        self.request = MagicMock()
        self.request.user = create_fake_user(
            character_id=1002,
            character_name="Test User",
            permissions=["aasrp.basic_access"],
        )
        # Use a real SrpLink instance
        self.srp_link = SrpLink.objects.create(
            srp_code="SRP123",
            fleet_time=datetime.now(),
            srp_name="Test SRP",
            fleet_doctrine="Doctrine A",
            aar_link="http://example.com/aar",
        )
        self.killmail_link = "https://zkillboard.com/kill/12345678/"
        self.ship_type_id = 123
        self.ship_value = 1000000
        self.victim_id = 456
        self.additional_info = "Additional information"

    @patch("aasrp.views.general.EveCharacter.objects.get_character_by_id")
    @patch("aasrp.views.general.esi")
    @patch("aasrp.views.general.SrpRequest.objects.create")
    @patch("aasrp.views.general.RequestComment.objects.bulk_create")
    @patch("aasrp.views.general.SrpRequest.objects.get_insurance_for_ship_type")
    @patch("aasrp.views.general.Insurance.objects.bulk_create")
    def test_creates_srp_request_successfully(
        self,
        mock_insurance_bulk_create,
        mock_get_insurance,
        mock_comment_bulk_create,
        mock_srp_request_create,
        mock_esi,
        mock_get_character_by_id,
    ):
        """
        Test that _save_srp_request creates an SrpRequest successfully.

        :param mock_insurance_bulk_create:
        :type mock_insurance_bulk_create:
        :param mock_get_insurance:
        :type mock_get_insurance:
        :param mock_comment_bulk_create:
        :type mock_comment_bulk_create:
        :param mock_srp_request_create:
        :type mock_srp_request_create:
        :param mock_esi:
        :type mock_esi:
        :param mock_get_character_by_id:
        :type mock_get_character_by_id:
        :return:
        :rtype:
        """

        mock_character = MagicMock()
        mock_get_character_by_id.return_value = mock_character

        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"
        mock_esi.client.Universe.GetUniverseTypesTypeId.return_value.result.return_value = (
            mock_ship
        )

        # Use a real SrpRequest instance for the mock
        real_srp_request = SrpRequest()
        mock_srp_request_create.return_value = real_srp_request

        mock_insurance = MagicMock()
        mock_get_insurance.return_value.levels = [mock_insurance]

        result = _save_srp_request(
            request=self.request,
            srp_link=self.srp_link,
            killmail_link=self.killmail_link,
            ship_type_id=self.ship_type_id,
            ship_value=self.ship_value,
            victim_id=self.victim_id,
            additional_info=self.additional_info,
        )

        self.assertEqual(result, real_srp_request)
        mock_get_character_by_id.assert_called_once_with(character_id=self.victim_id)
        mock_esi.client.Universe.GetUniverseTypesTypeId.assert_called_once_with(
            type_id=self.ship_type_id
        )
        mock_srp_request_create.assert_called_once()
        mock_comment_bulk_create.assert_called_once()
        mock_get_insurance.assert_called_once_with(ship_type_id=self.ship_type_id)
        mock_insurance_bulk_create.assert_called_once()

    @patch("aasrp.views.general.EveCharacter.objects.get_character_by_id")
    def test_handles_invalid_character_id(self, mock_get_character_by_id):
        """
        Test that _save_srp_request handles an invalid character ID.

        :param mock_get_character_by_id:
        :type mock_get_character_by_id:
        :return:
        :rtype:
        """

        mock_get_character_by_id.side_effect = ValueError("Invalid character ID")

        with self.assertRaises(ValueError):
            _save_srp_request(
                request=self.request,
                srp_link=self.srp_link,
                killmail_link=self.killmail_link,
                ship_type_id=self.ship_type_id,
                ship_value=self.ship_value,
                victim_id=self.victim_id,
                additional_info=self.additional_info,
            )

    @patch("aasrp.views.general.esi")
    def test_handles_invalid_ship_type_id(self, mock_esi):
        """
        Test that _save_srp_request handles an invalid ship type ID.

        :param mock_esi:
        :type mock_esi:
        :return:
        :rtype:
        """

        mock_esi.client.Universe.GetUniverseTypesTypeId.side_effect = ValueError(
            "Invalid ship type ID"
        )

        with self.assertRaises(ValueError):
            _save_srp_request(
                request=self.request,
                srp_link=self.srp_link,
                killmail_link=self.killmail_link,
                ship_type_id=self.ship_type_id,
                ship_value=self.ship_value,
                victim_id=self.victim_id,
                additional_info=self.additional_info,
            )

    @patch("aasrp.views.general.esi")
    @patch("aasrp.views.general.SrpRequest.objects.get_insurance_for_ship_type")
    def test_handles_missing_insurance_information(self, mock_get_insurance, mock_esi):
        mock_ship = MagicMock()
        mock_ship.name = "Test Ship"  # Ensure this is a string
        mock_esi.client.Universe.GetUniverseTypesTypeId.return_value.result.return_value = (
            mock_ship
        )
        mock_get_insurance.return_value.levels = []

        result = _save_srp_request(
            request=self.request,
            srp_link=self.srp_link,
            killmail_link=self.killmail_link,
            ship_type_id=self.ship_type_id,
            ship_value=self.ship_value,
            victim_id=self.victim_id,
            additional_info=self.additional_info,
        )

        self.assertIsNotNone(result)
        mock_get_insurance.assert_called_once_with(ship_type_id=self.ship_type_id)
