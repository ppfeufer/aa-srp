# Standard Library
from datetime import datetime
from http import HTTPStatus
from unittest.mock import patch

# Django
from django.contrib import messages
from django.contrib.auth.models import Permission, User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

# AA SRP
from aasrp.models import SrpLink
from aasrp.tests.utils import get_permission_content_type
from aasrp.views.general import (
    complete_srp_link,
    delete_srp_link,
    disable_srp_link,
    enable_srp_link,
    request_srp,
    srp_link_view_requests,
)


class TestSrpLinkDelete(TestCase):
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

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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
        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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


class TestSrpLinkDisable(TestCase):
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

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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


class TestSrpLinkEnable(TestCase):
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

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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
        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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


class TestSrpLinkViewRequests(TestCase):
    """
    Test the srp_link_view_requests view.
    """

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_view_requests_srp_link_not_found(self, mock_get_srp_link):
        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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


class TestCompleteSrpLink(TestCase):
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

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp"
        )
        user.user_permissions.add(permission)
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


class TestRequestSrp(TestCase):
    """
    Test the request_srp view.
    """

    @patch("aasrp.views.general.SrpLink.objects.get")
    def test_request_srp_link_not_found(self, mock_get_srp_link):
        """
        Test the request_srp view for a user with the basic_access permissions and not found.

        :param mock_get_srp_link:
        :type mock_get_srp_link:
        :return:
        :rtype:
        """

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="basic_access"
        )
        user.user_permissions.add(permission)
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

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="basic_access"
        )
        user.user_permissions.add(permission)
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
