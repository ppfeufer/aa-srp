# Django
from django.contrib.auth.models import Permission, User
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import SafeString

# AA SRP
from aasrp.helper.icons import (
    copy_to_clipboard_icon,
    dashboard_action_icons,
    get_srp_request_action_icons,
    get_srp_request_status_icon,
)
from aasrp.models import SrpLink, SrpRequest
from aasrp.tests.utils import get_permission_content_type


class CopyToClipboardIconTests(TestCase):
    """
    Test cases for the copy_to_clipboard_icon function.
    """

    def test_copy_to_clipboard_icon_renders_correctly(self):
        """
        Test that the copy_to_clipboard_icon function renders the correct HTML.

        :return:
        :rtype:
        """

        data = "Sample data"
        title = "Copy this data"
        expected_html = render_to_string(
            template_name="aasrp/partials/common/copy-to-clipboard-icon.html",
            context={"data": data, "title": title},
        )

        result = copy_to_clipboard_icon(data, title)

        self.assertIsInstance(result, SafeString)
        self.assertEqual(result, expected_html)

    def test_copy_to_clipboard_icon_handles_empty_data(self):
        """
        Test that the copy_to_clipboard_icon function handles empty data correctly.

        :return:
        :rtype:
        """

        data = ""
        title = "Copy this data"
        expected_html = render_to_string(
            template_name="aasrp/partials/common/copy-to-clipboard-icon.html",
            context={"data": data, "title": title},
        )

        result = copy_to_clipboard_icon(data, title)

        self.assertIsInstance(result, SafeString)
        self.assertEqual(result, expected_html)

    def test_copy_to_clipboard_icon_handles_empty_title(self):
        """
        Test that the copy_to_clipboard_icon function handles empty title correctly.

        :return:
        :rtype:
        """

        data = "Sample data"
        title = ""
        expected_html = render_to_string(
            template_name="aasrp/partials/common/copy-to-clipboard-icon.html",
            context={"data": data, "title": title},
        )

        result = copy_to_clipboard_icon(data, title)

        self.assertIsInstance(result, SafeString)
        self.assertEqual(result, expected_html)

    def test_copy_to_clipboard_icon_handles_special_characters(self):
        """
        Test that the copy_to_clipboard_icon function handles special characters correctly.

        :return:
        :rtype:
        """

        data = "<script>alert('test');</script>"
        title = "Copy <script> tag"
        expected_html = render_to_string(
            template_name="aasrp/partials/common/copy-to-clipboard-icon.html",
            context={"data": data, "title": title},
        )

        result = copy_to_clipboard_icon(data, title)

        self.assertIsInstance(result, SafeString)
        self.assertEqual(result, expected_html)


class TestGetSrpRequestActionIcons(TestCase):
    """
    Test cases for the get_srp_request_action_icons function.
    """

    def test_srp_request_action_icons_for_active_srp_link_with_manage_srp(self):
        """
        Test that the get_srp_request_action_icons function returns the correct icons
        for SRP requests for an active SRP link and a user with the manage_srp permission.

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
            srp_name="Test SRP",
            srp_status=SrpLink.Status.ACTIVE,
            fleet_time=timezone.now(),  # Add a valid fleet_time
            srp_code="test_srp_code",  # Add a valid srp_code
        )
        srp_request = SrpRequest.objects.create(
            srp_link=srp_link,
            request_status=SrpRequest.Status.PENDING,
            request_code="test_srp_request_code",  # Add a valid srp_request_code
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_action_icons(request, srp_link, srp_request)

        view_kwargs = {
            "srp_code": "test_srp_code",
            "srp_request_code": "test_srp_request_code",
        }

        # SRP Info
        self.assertIn("fa-solid fa-circle-info", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_additional_information", kwargs=view_kwargs)}"',
            result,
        )

        # Approve
        self.assertIn("fa-solid fa-check", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_approve", kwargs=view_kwargs)}"',
            result,
        )

        # Deny
        self.assertIn("fa-solid fa-ban", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_deny", kwargs=view_kwargs)}"',
            result,
        )

        # Remove
        self.assertIn("fa-solid fa-trash-can", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_remove", kwargs=view_kwargs)}"',
            result,
        )

    def test_srp_request_action_icons_for_active_srp_link_with_manage_srp_requests(
        self,
    ):
        """
        Test that the get_srp_request_action_icons function returns the correct icons
        for SRP requests for an active SRP link and a user with the manage_srp_requests permission.

        :return:
        :rtype:
        """

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp_requests"
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            srp_status=SrpLink.Status.ACTIVE,
            fleet_time=timezone.now(),  # Add a valid fleet_time
            srp_code="test_srp_code",  # Add a valid srp_code
        )
        srp_request = SrpRequest.objects.create(
            srp_link=srp_link,
            request_status=SrpRequest.Status.PENDING,
            request_code="test_srp_request_code",  # Add a valid srp_request_code
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_action_icons(request, srp_link, srp_request)

        view_kwargs = {
            "srp_code": "test_srp_code",
            "srp_request_code": "test_srp_request_code",
        }

        # SRP Info
        self.assertIn("fa-solid fa-circle-info", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_additional_information", kwargs=view_kwargs)}"',
            result,
        )

        # Approve
        self.assertIn("fa-solid fa-check", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_approve", kwargs=view_kwargs)}"',
            result,
        )

        # Deny
        self.assertIn("fa-solid fa-ban", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_deny", kwargs=view_kwargs)}"',
            result,
        )

        # Remove
        self.assertNotIn("fa-solid fa-trash-can", result)
        self.assertNotIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_remove", kwargs=view_kwargs)}"',
            result,
        )

    def test_srp_request_action_icons_for_closed_srp_link_with_manage_srp(self):
        """
        Test that the get_srp_request_action_icons function returns the correct icons
        for SRP requests for a closed SRP link and a user with the manage_srp permission.

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
            srp_name="Test SRP",
            srp_status=SrpLink.Status.CLOSED,
            fleet_time=timezone.now(),  # Add a valid fleet_time
            srp_code="test_srp_code",  # Add a valid srp_code
        )
        srp_request = SrpRequest.objects.create(
            srp_link=srp_link,
            request_status=SrpRequest.Status.APPROVED,
            request_code="test_srp_request_code",  # Add a valid srp_request_code
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_action_icons(request, srp_link, srp_request)

        view_kwargs = {
            "srp_code": "test_srp_code",
            "srp_request_code": "test_srp_request_code",
        }

        # SRP Info
        self.assertIn("fa-solid fa-circle-info", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_additional_information", kwargs=view_kwargs)}"',
            result,
        )

        # Approve
        self.assertIn("fa-solid fa-check", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_approve", kwargs=view_kwargs)}"',
            result,
        )

        # Deny
        self.assertIn("fa-solid fa-ban", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_deny", kwargs=view_kwargs)}"',
            result,
        )

        # Remove
        self.assertIn("fa-solid fa-trash-can", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_remove", kwargs=view_kwargs)}"',
            result,
        )

    def test_srp_request_action_icons_for_closed_srp_link_with_manage_srp_requests(
        self,
    ):
        """
        Test that the get_srp_request_action_icons function returns the correct icons
        for SRP requests for a closed SRP link and a user with the manage_srp_requests permission.

        :return:
        :rtype:
        """

        permission_content_type = get_permission_content_type()

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=permission_content_type, codename="manage_srp_requests"
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            srp_status=SrpLink.Status.CLOSED,
            fleet_time=timezone.now(),  # Add a valid fleet_time
            srp_code="test_srp_code",  # Add a valid srp_code
        )
        srp_request = SrpRequest.objects.create(
            srp_link=srp_link,
            request_status=SrpRequest.Status.APPROVED,
            request_code="test_srp_request_code",  # Add a valid srp_request_code
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_action_icons(request, srp_link, srp_request)

        view_kwargs = {
            "srp_code": "test_srp_code",
            "srp_request_code": "test_srp_request_code",
        }

        # SRP Info
        self.assertIn("fa-solid fa-circle-info", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_additional_information", kwargs=view_kwargs)}"',
            result,
        )

        # Approve
        self.assertIn("fa-solid fa-check", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_approve", kwargs=view_kwargs)}"',
            result,
        )

        # Deny
        self.assertIn("fa-solid fa-ban", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_deny", kwargs=view_kwargs)}"',
            result,
        )

        # Remove
        self.assertNotIn("fa-solid fa-trash-can", result)
        self.assertNotIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_remove", kwargs=view_kwargs)}"',
            result,
        )

    def test_srp_request_action_icons_for_completed_srp_link(self):
        """
        Test that the get_srp_request_action_icons function returns the correct icons for SRP requests for a completed SRP link.

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
            srp_name="Test SRP",
            srp_status=SrpLink.Status.COMPLETED,
            fleet_time=timezone.now(),  # Add a valid fleet_time
            srp_code="test_srp_code",  # Add a valid srp_code
        )
        srp_request = SrpRequest.objects.create(
            srp_link=srp_link,
            request_status=SrpRequest.Status.APPROVED,
            request_code="test_srp_request_code",  # Add a valid srp_request_code
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_action_icons(request, srp_link, srp_request)

        view_kwargs = {
            "srp_code": "test_srp_code",
            "srp_request_code": "test_srp_request_code",
        }

        # SRP Info
        self.assertIn("fa-solid fa-circle-info", result)
        self.assertIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_additional_information", kwargs=view_kwargs)}"',
            result,
        )

        # Approve
        self.assertNotIn("fa-solid fa-check", result)
        self.assertNotIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_approve", kwargs=view_kwargs)}"',
            result,
        )

        # Deny
        self.assertNotIn("fa-solid fa-ban", result)
        self.assertNotIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_deny", kwargs=view_kwargs)}"',
            result,
        )

        # Remove
        self.assertNotIn("fa-solid fa-trash-can", result)
        self.assertNotIn(
            f'data-link="{reverse("aasrp:ajax_srp_request_remove", kwargs=view_kwargs)}"',
            result,
        )

    def test_srp_request_action_icons_for_user_without_permission(self):
        user = User.objects.create(username="testuser")
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            srp_status=SrpLink.Status.ACTIVE,
            fleet_time=timezone.now(),  # Add a valid fleet_time
            srp_code="test_srp_code",  # Add a valid srp_code
        )
        srp_request = SrpRequest.objects.create(
            srp_link=srp_link,
            request_status=SrpRequest.Status.PENDING,
            request_code="test_srp_request_code",  # Add a valid srp_request_code
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_action_icons(request, srp_link, srp_request)

        self.assertNotIn("fa-hand-holding-dollar", result)
        self.assertNotIn("fa-eye", result)
        self.assertNotIn("fa-newspaper", result)
        self.assertNotIn("fa-ban", result)
        self.assertNotIn("fa-trash-can", result)


class TestGetSrpRequestStatusIcon(TestCase):
    """
    Test cases for the get_srp_request_status_icon function.
    """

    def test_srp_request_status_icon_for_pending_request(self):
        """
        Test that the get_srp_request_status_icon function returns the correct icon for pending requests.

        :return:
        :rtype:
        """

        user = User.objects.create(username="testuser")
        self.client.force_login(user)

        srp_request = SrpRequest.objects.create(
            srp_link=SrpLink.objects.create(
                srp_name="Test SRP",
                srp_status=SrpLink.Status.ACTIVE,
                fleet_time=timezone.now(),
                srp_code="test_srp_code",
            ),
            request_status=SrpRequest.Status.PENDING,
            request_code="test_srp_request_code",
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_status_icon(request, srp_request)

        self.assertIn("btn-info", result)
        self.assertIn("fa-clock", result)
        self.assertIn("SRP request pending", result)

    def test_srp_request_status_icon_for_approved_request(self):
        """
        Test that the get_srp_request_status_icon function returns the correct icon for approved requests.

        :return:
        :rtype:
        """

        user = User.objects.create(username="testuser")
        self.client.force_login(user)

        srp_request = SrpRequest.objects.create(
            srp_link=SrpLink.objects.create(
                srp_name="Test SRP",
                srp_status=SrpLink.Status.ACTIVE,
                fleet_time=timezone.now(),
                srp_code="test_srp_code",
            ),
            request_status=SrpRequest.Status.APPROVED,
            request_code="test_srp_request_code",
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_status_icon(request, srp_request)

        self.assertIn("btn-success", result)
        self.assertIn("fa-thumbs-up", result)
        self.assertIn("SRP request approved", result)

    def test_srp_request_status_icon_for_rejected_request(self):
        """
        Test that the get_srp_request_status_icon function returns the correct icon for rejected requests.

        :return:
        :rtype:
        """

        user = User.objects.create(username="testuser")
        self.client.force_login(user)

        srp_request = SrpRequest.objects.create(
            srp_link=SrpLink.objects.create(
                srp_name="Test SRP",
                srp_status=SrpLink.Status.ACTIVE,
                fleet_time=timezone.now(),
                srp_code="test_srp_code",
            ),
            request_status=SrpRequest.Status.REJECTED,
            request_code="test_srp_request_code",
        )

        # Create a request object
        request = self.client.get(
            reverse("aasrp:view_srp_requests", kwargs={"srp_code": "test_srp_code"})
        ).wsgi_request

        result = get_srp_request_status_icon(request, srp_request)

        self.assertIn("btn-danger", result)
        self.assertIn("fa-thumbs-down", result)
        self.assertIn("SRP request rejected", result)


class TestDashboardActionIcons(TestCase):
    """
    Test cases for the dashboard action icons.
    """

    def test_dashboard_action_icons_for_active_srp_link_with_manage_srp(self):
        """
        Test that the dashboard_action_icons function returns the correct icons for
        active SRP links and a user with the manage_srp permission.

        :return:
        :rtype:
        """

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=get_permission_content_type(), codename="manage_srp"
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            srp_status=SrpLink.Status.ACTIVE,
            fleet_time=timezone.now(),
            srp_code="test_srp_code",
        )

        # Create a request object
        request = self.client.get(reverse("aasrp:srp_links")).wsgi_request
        result = dashboard_action_icons(request, srp_link)

        self.assertIn("fa-solid fa-hand-holding-dollar", result)
        self.assertIn("fa-solid fa-eye", result)
        self.assertIn("fa-regular fa-newspaper", result)
        self.assertIn("fa-solid fa-ban", result)
        self.assertIn("fa-regular fa-trash-can", result)

    def test_dashboard_action_icons_for_active_srp_link_without_manage_permissions(
        self,
    ):
        """
        Test that the dashboard_action_icons function returns the correct icons for
        active SRP links and a user without the manage_srp permission.

        :return:
        :rtype:
        """

        user = User.objects.create(username="testuser")
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            srp_status=SrpLink.Status.ACTIVE,
            fleet_time=timezone.now(),
            srp_code="test_srp_code",
        )

        # Create a request object
        request = self.client.get(reverse("aasrp:srp_links")).wsgi_request
        result = dashboard_action_icons(request, srp_link)

        self.assertIn("fa-solid fa-hand-holding-dollar", result)
        self.assertNotIn("fa-solid fa-eye", result)
        self.assertNotIn("fa-regular fa-newspaper", result)
        self.assertNotIn("fa-solid fa-ban", result)
        self.assertNotIn("fa-regular fa-trash-can", result)

    def test_dashboard_action_icons_for_closed_srp_link_with_manage_srp(self):
        """
        Test that the dashboard_action_icons function returns the correct icons for
        closed SRP links and a user with the manage_srp permission.

        :return:
        :rtype:
        """

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=get_permission_content_type(), codename="manage_srp"
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            srp_status=SrpLink.Status.CLOSED,
            fleet_time=timezone.now(),
            srp_code="test_srp_code",
        )

        # Create a request object
        request = self.client.get(reverse("aasrp:srp_links")).wsgi_request
        result = dashboard_action_icons(request, srp_link)

        self.assertIn("fa-solid fa-eye", result)
        self.assertIn("fa-solid fa-check", result)
        self.assertIn("fa-regular fa-trash-can", result)

    def test_dashboard_action_icons_for_completed_srp_link_with_manage_srp(self):
        """
        Test that the dashboard_action_icons function returns the correct icons for
        completed SRP links and a user with the manage_srp permission.

        :return:
        :rtype:
        """

        user = User.objects.create(username="testuser")
        permission = Permission.objects.get(
            content_type=get_permission_content_type(), codename="manage_srp"
        )
        user.user_permissions.add(permission)
        self.client.force_login(user)

        srp_link = SrpLink.objects.create(
            srp_name="Test SRP",
            srp_status=SrpLink.Status.COMPLETED,
            fleet_time=timezone.now(),
            srp_code="test_srp_code",
        )

        # Create a request object
        request = self.client.get(reverse("aasrp:srp_links")).wsgi_request
        result = dashboard_action_icons(request, srp_link)

        self.assertIn("fa-solid fa-eye", result)
        self.assertNotIn("fa-regular fa-newspaper", result)
        self.assertNotIn("fa-solid fa-ban", result)
        self.assertNotIn("fa-regular fa-trash-can", result)
