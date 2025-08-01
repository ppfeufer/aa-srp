# Standard Library
import json
from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

# Django
from django.contrib.auth.models import Permission, User
from django.test import RequestFactory, TestCase
from django.urls import reverse

# AA SRP
from aasrp.models import SrpLink, SrpRequest
from aasrp.tests.utils import get_permission_content_type
from aasrp.views.ajax import srp_request_remove, srp_requests_bulk_approve


class TestSrpRequestRemove(TestCase):
    """
    Test the srp_request_remove view.
    """

    @patch("aasrp.views.ajax.SrpRequest.objects.get")
    def test_srp_request_remove_success_for_user_with_perm_manage_srp(self, mock_get):
        """
        Test the srp_request_remove view for a user with the manage_srp permissions.

        :param mock_get:
        :type mock_get:
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
        srp_request = SrpRequest.objects.create(
            request_code="REQ123", srp_link=srp_link
        )
        srp_request.delete = MagicMock()
        mock_get.return_value = srp_request

        factory = RequestFactory()
        request = factory.get(
            reverse("aasrp:ajax_srp_request_remove", args=["SRP123", "REQ123"])
        )
        request.user = user

        response = srp_request_remove(request, "SRP123", "REQ123")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(
            response.content,
            {"success": True, "message": "SRP request has been removed"},
        )
        srp_request.delete.assert_called_once()

    @patch("aasrp.views.ajax.SrpRequest.objects.get")
    def test_srp_request_remove_success_for_user_with_perm_manage_srp_requests(
        self, mock_get
    ):
        """
        Test the srp_request_remove view for a user with the manage_srp_requests permissions.

        :param mock_get:
        :type mock_get:
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
        srp_link = SrpLink.objects.create(srp_code="SRP123", fleet_time=datetime.now())
        srp_request = SrpRequest.objects.create(
            request_code="REQ123", srp_link=srp_link
        )
        srp_request.delete = MagicMock()
        mock_get.return_value = srp_request

        factory = RequestFactory()
        request = factory.get(
            reverse("aasrp:ajax_srp_request_remove", args=["SRP123", "REQ123"])
        )
        request.user = user

        response = srp_request_remove(request, "SRP123", "REQ123")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(
            response.content,
            {"success": True, "message": "SRP request has been removed"},
        )
        srp_request.delete.assert_called_once()

    @patch("aasrp.views.ajax.SrpRequest.objects.get")
    def test_srp_request_remove_not_found_for_user_with_perm_manage_srp(self, mock_get):
        """
        Test the srp_request_remove view for a user with the manage_srp permissions

        :param mock_get:
        :type mock_get:
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
        mock_get.side_effect = SrpRequest.DoesNotExist

        factory = RequestFactory()
        request = factory.get(
            reverse("aasrp:ajax_srp_request_remove", args=["SRP123", "REQ123"])
        )
        request.user = user

        response = srp_request_remove(request, "SRP123", "REQ123")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(
            response.content,
            {"success": False, "message": "No matching SRP request found"},
        )

    @patch("aasrp.views.ajax.SrpRequest.objects.get")
    def test_srp_request_remove_not_found_for_user_with_perm_manage_srp_requests(
        self, mock_get
    ):
        """
        Test the srp_request_remove view for a user with the manage_srp_requests permissions

        :param mock_get:
        :type mock_get:
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
        mock_get.side_effect = SrpRequest.DoesNotExist

        factory = RequestFactory()
        request = factory.get(
            reverse("aasrp:ajax_srp_request_remove", args=["SRP123", "REQ123"])
        )
        request.user = user

        response = srp_request_remove(request, "SRP123", "REQ123")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(
            response.content,
            {"success": False, "message": "No matching SRP request found"},
        )


class MockSrpRequest:
    def __init__(self, request_code, payout_amount, loss_amount):
        self.request_code = request_code
        self.payout_amount = payout_amount
        self.loss_amount = loss_amount

    def save(self):
        pass


class TestSrpRequestsBulkApprove(TestCase):
    """
    Test the bulk approval of SRP requests.
    """

    def test_approves_multiple_requests_successfully(self):
        """
        Test the bulk approval of multiple SRP requests.

        :return:
        :rtype:
        """

        # Mock the request object
        request = MagicMock()
        request.method = "POST"
        request.POST.getlist.return_value = ["REQUEST_CODE_1", "REQUEST_CODE_2"]

        # Mock the srp_requests QuerySet
        srp_requests = MagicMock()
        srp_requests.count.return_value = 2
        srp_requests.exists.return_value = True

        # Patch the filter method to return the mocked srp_requests
        with patch("aasrp.models.SrpRequest.objects.filter", return_value=srp_requests):
            response = srp_requests_bulk_approve(request, "SRP_CODE")

            # Parse the response content
            response_data = json.loads(response.content)

            # Assert the response
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response_data["success"])
