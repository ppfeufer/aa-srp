"""
Tests for AJAX views in the aasrp app.
"""

# Standard Library
import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

# Third Party
from eve_sde.models import ItemType

# Django
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

# AA SRP
from aasrp.models import RequestComment, SrpLink, SrpRequest
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_fake_user, random_id
from aasrp.views.ajax import (
    srp_link_update_total_cost,
    srp_request_approve,
    srp_request_deny,
    srp_request_remove,
    srp_requests_bulk_approve,
    srp_requests_bulk_remove,
)


class BaseViewsTestCase(BaseTestCase):
    """
    Base test case for views tests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the test class by creating fake users.

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.user_jean_luc_picard = create_fake_user(
            character_id=random_id(),
            character_name="Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )
        cls.user_wesley_crusher = create_fake_user(
            character_id=random_id(),
            character_name="Wesley Crusher",
            permissions=["aasrp.basic_access"],
        )

        cls.srp_link_active = SrpLink(
            srp_name="Active SRP",
            srp_status=SrpLink.Status.ACTIVE,
            creator=cls.user_jean_luc_picard,
            fleet_time=timezone.now(),
            srp_code=get_random_string(length=16),
        )
        cls.srp_link_active.save()

        cls.srp_link_closed = SrpLink(
            srp_name="Closed SRP",
            srp_status=SrpLink.Status.CLOSED,
            creator=cls.user_jean_luc_picard,
            fleet_time=timezone.now(),
            srp_code=get_random_string(length=16),
        )
        cls.srp_link_closed.save()

        cls.ship_test = ItemType.objects.create(name="Test Ship", id=12345)
        cls.srp_request_pending = SrpRequest.objects.create(
            srp_link=cls.srp_link_active,
            creator=cls.user_wesley_crusher,
            request_code=get_random_string(length=16),
            request_status=SrpRequest.Status.PENDING,
            loss_amount=100,
            ship=cls.ship_test,
        )
        cls.srp_request_pending.save()


class TestSrpRequestsBulkRemove(BaseViewsTestCase):
    """
    Tests for the srp_requests_bulk_remove view.
    """

    @patch("aasrp.models.SrpRequest.objects.filter")
    def test_returns_success_when_valid_request_codes_provided(self, mock_filter):
        """
        Test that the view returns success when valid SRP request codes are provided.

        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_qs = MagicMock()
        mock_qs.exists.return_value = True
        mock_qs.delete.return_value = None
        mock_qs.count.return_value = 0
        mock_filter.return_value = mock_qs

        request = MagicMock(
            method="POST", body=json.dumps({"srp_request_codes": ["code1", "code2"]})
        )
        response = srp_requests_bulk_remove(request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {
                "success": True,
                "message": "SRP requests have been removed",
                "pending_requests": 0,
            },
        )

    @patch("aasrp.models.SrpRequest.objects.filter")
    def test_returns_error_when_no_matching_requests_found(self, mock_filter):
        """
        Test that the view returns an error when no matching SRP requests are found.

        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_filter.return_value.exists.return_value = False

        request = MagicMock(
            method="POST", body=json.dumps({"srp_request_codes": ["code1", "code2"]})
        )
        response = srp_requests_bulk_remove(request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "No matching SRP requests found"},
        )

    def test_returns_error_when_request_method_is_not_post(self):
        """
        Test that the view returns an error when the request method is not POST.

        :return:
        :rtype:
        """

        request = MagicMock(method="GET")
        response = srp_requests_bulk_remove(request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid request method"},
        )

    def test_returns_error_when_invalid_form_data_provided(self):
        """
        Test that the view returns an error when invalid form data is provided.

        :return:
        :rtype:
        """

        request = MagicMock(method="POST", body=json.dumps({}))
        response = srp_requests_bulk_remove(request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid form data"},
        )


class TestSrpRequestRemove(BaseViewsTestCase):
    """
    Tests for the srp_request_remove view.
    """

    @patch("aasrp.models.SrpRequest.objects.get")
    def test_returns_success_when_request_is_removed(self, mock_get):
        """
        Test that the view returns success when the SRP request is removed.

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_get.return_value.delete.return_value = None

        request = MagicMock()
        response = srp_request_remove(request, "valid_srp_code", "valid_request_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {
                "success": True,
                "message": "SRP request has been removed",
                "pending_requests": 1,
            },
        )

    @patch("aasrp.models.SrpRequest.objects.get")
    def test_returns_error_when_request_does_not_exist(self, mock_get):
        mock_get.side_effect = SrpRequest.DoesNotExist

        request = MagicMock()
        response = srp_request_remove(request, "valid_srp_code", "invalid_request_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "No matching SRP request found"},
        )


class TestSrpRequestDeny(BaseViewsTestCase):
    """
    Tests for the srp_request_deny view.
    """

    @patch("aasrp.models.SrpRequest.objects.get")
    @patch("aasrp.views.ajax.SrpRequestRejectForm")
    @patch("aasrp.views.ajax.get_user_settings")
    @patch("aasrp.views.ajax.notify_requester")
    def test_returns_success_when_request_is_denied(
        self, mock_notify, mock_get_user_settings, mock_form, mock_get
    ):
        """
        Test that the view returns success when the SRP request is denied.

        :param mock_notify:
        :type mock_notify:
        :param mock_get_user_settings:
        :type mock_get_user_settings:
        :param mock_form:
        :type mock_form:
        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        # Create a valid SrpRequest using only required fields
        srp_request = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_jean_luc_picard,
        )
        mock_get.return_value = srp_request
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = {"comment": "Rejection reason"}
        mock_get_user_settings.return_value.disable_notifications = False

        request = MagicMock(
            method="POST", body=json.dumps({"comment": "Rejection reason"})
        )
        request.user = self.user_jean_luc_picard

        response = srp_request_deny(
            request, srp_request.srp_link.srp_code, srp_request.request_code
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {
                "success": True,
                "message": "SRP request has been rejected",
                "pending_requests": 1,
            },
        )
        mock_notify.assert_called_once()

    @patch("aasrp.models.SrpRequest.objects.get")
    @patch("aasrp.views.ajax.SrpRequestRejectForm")
    @patch("aasrp.views.ajax.get_user_settings")
    @patch("aasrp.views.ajax.notify_requester")
    def test_does_not_notify_requester_when_notifications_are_disabled(
        self, mock_notify, mock_get_user_settings, mock_form, mock_get
    ):
        """
        Test that the view does not notify the requester when notifications are disabled.

        :param mock_notify:
        :type mock_notify:
        :param mock_get_user_settings:
        :type mock_get_user_settings:
        :param mock_form:
        :type mock_form:
        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        srp_request = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_jean_luc_picard,
        )
        mock_get.return_value = srp_request
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = {"comment": "Rejection reason"}
        mock_get_user_settings.return_value.disable_notifications = True

        request = MagicMock(
            method="POST", body=json.dumps({"comment": "Rejection reason"})
        )
        request.user = self.user_jean_luc_picard

        response = srp_request_deny(
            request, srp_request.srp_link.srp_code, srp_request.request_code
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {
                "success": True,
                "message": "SRP request has been rejected",
                "pending_requests": 1,
            },
        )
        mock_notify.assert_not_called()

    @patch("aasrp.models.SrpRequest.objects.get")
    def test_returns_error_when_request_does_not_exist(self, mock_get):
        """
        Test that the view returns an error when the SRP request does not exist.

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_get.side_effect = SrpRequest.DoesNotExist

        request = MagicMock(
            method="POST", body=json.dumps({"comment": "Rejection reason"})
        )
        response = srp_request_deny(request, "valid_srp_code", "invalid_request_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "No matching SRP request found"},
        )

    @patch("aasrp.models.SrpRequest.objects.get")
    @patch("aasrp.views.ajax.SrpRequestRejectForm")
    def test_returns_error_when_form_data_is_invalid(self, mock_form, mock_get):
        """
        Test that the view returns an error when the form data is invalid.

        :param mock_form:
        :type mock_form:
        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_get.return_value = MagicMock()
        mock_form.return_value.is_valid.return_value = False

        request = MagicMock(method="POST", body=json.dumps({"comment": ""}))
        response = srp_request_deny(request, "valid_srp_code", "valid_request_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid form data"},
        )

    @patch("aasrp.models.SrpRequest.objects.get")
    def test_returns_error_when_request_method_is_not_post(self, mock_get):
        """
        Test that the view returns an error when the request method is not POST.

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        srp_request = self.srp_request_pending
        mock_get.return_value = srp_request

        request = MagicMock(method="GET")
        response = srp_request_deny(request, "valid_srp_code", "valid_request_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid request method"},
        )


class TestSrpRequestsBulkApprove(BaseViewsTestCase):
    """
    Tests for the srp_requests_bulk_approve view.
    """

    @patch("aasrp.models.SrpRequest.objects.filter")
    @patch("aasrp.models.SrpRequest.objects.bulk_update")
    @patch("aasrp.models.RequestComment.objects.bulk_create")
    @patch("aasrp.views.ajax.get_user_settings")
    @patch("aasrp.views.ajax.notify_requester")
    def test_returns_success_when_bulk_approval_is_successful(
        self,
        mock_notify,
        mock_get_user_settings,
        mock_bulk_create,
        mock_bulk_update,
        mock_filter,
    ):
        """
        Test that the view returns success when bulk approval is successful.

        :param mock_notify:
        :type mock_notify:
        :param mock_get_user_settings:
        :type mock_get_user_settings:
        :param mock_bulk_create:
        :type mock_bulk_create:
        :param mock_bulk_update:
        :type mock_bulk_update:
        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_request = MagicMock(
            method="POST", body=json.dumps({"srp_request_codes": ["code1", "code2"]})
        )
        mock_request.user = self.user_jean_luc_picard
        mock_get_user_settings.return_value.disable_notifications = False

        srp_request_1 = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_jean_luc_picard,
        )
        srp_request_2 = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_jean_luc_picard,
        )
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = [srp_request_1, srp_request_2]
        mock_queryset.count.return_value = 2
        mock_queryset.exists.return_value = True
        mock_filter.return_value = mock_queryset

        response = srp_requests_bulk_approve(mock_request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {
                "success": True,
                "message": "SRP requests have been approved",
                "pending_requests": 2,
            },
        )
        mock_bulk_update.assert_called_once()
        mock_bulk_create.assert_called_once()
        mock_notify.assert_called()

    @patch("aasrp.models.SrpRequest.objects.filter")
    @patch("aasrp.models.SrpRequest.objects.bulk_update")
    @patch("aasrp.models.RequestComment.objects.bulk_create")
    @patch("aasrp.views.ajax.get_user_settings")
    @patch("aasrp.views.ajax.notify_requester")
    def test_does_not_notify_requesters_with_notifications_disabled(
        self,
        mock_notify,
        mock_get_user_settings,
        mock_bulk_create,
        mock_bulk_update,
        mock_filter,
    ):
        """
        Test that bulk approval skips notifications when requesters disabled notifications.

        :param mock_notify:
        :type mock_notify:
        :param mock_get_user_settings:
        :type mock_get_user_settings:
        :param mock_bulk_create:
        :type mock_bulk_create:
        :param mock_bulk_update:
        :type mock_bulk_update:
        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_request = MagicMock(
            method="POST", body=json.dumps({"srp_request_codes": ["code1", "code2"]})
        )
        mock_request.user = self.user_jean_luc_picard
        mock_get_user_settings.return_value.disable_notifications = True

        srp_request_1 = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_jean_luc_picard,
            request_status=SrpRequest.Status.PENDING,
            loss_amount=100,
            ship=self.ship_test,
        )
        srp_request_2 = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_wesley_crusher,
            request_status=SrpRequest.Status.PENDING,
            loss_amount=200,
            ship=self.ship_test,
        )
        mock_queryset = MagicMock()
        mock_queryset.__iter__.return_value = [srp_request_1, srp_request_2]
        mock_queryset.count.return_value = 2
        mock_queryset.exists.return_value = True
        mock_filter.return_value = mock_queryset

        response = srp_requests_bulk_approve(mock_request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {
                "success": True,
                "message": "SRP requests have been approved",
                "pending_requests": 2,
            },
        )
        mock_bulk_update.assert_called_once()
        mock_bulk_create.assert_called_once()
        mock_notify.assert_not_called()

    @patch("aasrp.models.SrpRequest.objects.filter")
    def test_returns_error_when_no_matching_requests_found(self, mock_filter):
        """
        Test that the view returns an error when no matching SRP requests are found.

        :param mock_filter:
        :type mock_filter:
        :return:
        :rtype:
        """

        mock_request = MagicMock(
            method="POST", body=json.dumps({"srp_request_codes": ["invalid_code"]})
        )
        mock_request.user = self.user_jean_luc_picard
        mock_filter.return_value.exists.return_value = False

        response = srp_requests_bulk_approve(mock_request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "No matching SRP requests found"},
        )

    def test_returns_error_when_request_method_is_not_post(self):
        """
        Test that the view returns an error when the request method is not POST.

        :return:
        :rtype:
        """

        mock_request = MagicMock(method="GET")
        response = srp_requests_bulk_approve(mock_request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid request method"},
        )

    @patch("aasrp.models.SrpRequest.objects.filter")
    def test_returns_error_when_invalid_form_data_is_provided(self, mock_filter):
        mock_request = MagicMock(method="POST", body=json.dumps({}))
        mock_filter.return_value.exists.return_value = False

        response = srp_requests_bulk_approve(mock_request, "valid_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid form data"},
        )


class TestSrpRequestApprove(BaseViewsTestCase):
    """
    Tests for the srp_request_approve view.
    """

    @patch("aasrp.models.SrpRequest.objects.get")
    @patch("aasrp.models.RequestComment.objects.bulk_create")
    @patch("aasrp.views.ajax.get_user_settings")
    @patch("aasrp.views.ajax.notify_requester")
    def test_returns_success_when_request_is_approved(
        self, mock_notify, mock_get_user_settings, mock_bulk_create, mock_get
    ):
        """
        Test that the view returns success when the SRP request is approved.

        :param mock_notify:
        :type mock_notify:
        :param mock_get_user_settings:
        :type mock_get_user_settings:
        :param mock_bulk_create:
        :type mock_bulk_create:
        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_request = MagicMock(
            method="POST", body=json.dumps({"comment": "Approval comment"})
        )
        mock_request.user = self.user_jean_luc_picard
        mock_get_user_settings.return_value.disable_notifications = False

        srp_request = self.srp_request_pending
        mock_get.return_value = srp_request

        response = srp_request_approve(
            mock_request, "valid_srp_code", "valid_request_code"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {
                "success": True,
                "message": "SRP request has been approved",
                "pending_requests": 0,
            },
        )
        mock_bulk_create.assert_called_once()
        mock_notify.assert_called_once()

    @patch("aasrp.models.SrpRequest.objects.get")
    @patch("aasrp.models.RequestComment.objects.bulk_create")
    @patch("aasrp.views.ajax.get_user_settings")
    @patch("aasrp.views.ajax.notify_requester")
    @patch("aasrp.views.ajax.SrpRequestAcceptForm")
    def test_creates_only_status_change_comment_when_reviser_comment_is_empty(
        self,
        mock_form,
        mock_notify,
        mock_get_user_settings,
        mock_bulk_create,
        mock_get,
    ):
        """
        Test that approving without a reviser comment creates only the status-change comment.

        :param mock_form:
        :type mock_form:
        :param mock_notify:
        :type mock_notify:
        :param mock_get_user_settings:
        :type mock_get_user_settings:
        :param mock_bulk_create:
        :type mock_bulk_create:
        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_request = MagicMock(method="POST", body=json.dumps({"comment": ""}))
        mock_request.user = self.user_jean_luc_picard
        mock_get_user_settings.return_value.disable_notifications = False

        srp_request = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_wesley_crusher,
            request_status=SrpRequest.Status.PENDING,
            loss_amount=100,
            ship=self.ship_test,
        )
        mock_get.return_value = srp_request
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = {"comment": ""}

        response = srp_request_approve(
            mock_request, srp_request.srp_link.srp_code, srp_request.request_code
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(json.loads(response.content)["success"], True)
        comments = mock_bulk_create.call_args.args[0]
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].comment_type, RequestComment.Type.STATUS_CHANGE)
        mock_notify.assert_called_once()

    @patch("aasrp.models.SrpRequest.objects.get")
    @patch("aasrp.models.RequestComment.objects.bulk_create")
    @patch("aasrp.views.ajax.get_user_settings")
    @patch("aasrp.views.ajax.notify_requester")
    @patch("aasrp.views.ajax.SrpRequestAcceptForm")
    def test_does_not_notify_requester_when_notifications_are_disabled(
        self,
        mock_form,
        mock_notify,
        mock_get_user_settings,
        mock_bulk_create,
        mock_get,
    ):
        """
        Test that requester notification is skipped when requester disabled notifications.

        :param mock_form:
        :type mock_form:
        :param mock_notify:
        :type mock_notify:
        :param mock_get_user_settings:
        :type mock_get_user_settings:
        :param mock_bulk_create:
        :type mock_bulk_create:
        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_request = MagicMock(
            method="POST", body=json.dumps({"comment": "Looks good"})
        )
        mock_request.user = self.user_jean_luc_picard
        mock_get_user_settings.return_value.disable_notifications = True

        srp_request = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_wesley_crusher,
            request_status=SrpRequest.Status.PENDING,
            loss_amount=100,
            ship=self.ship_test,
        )
        mock_get.return_value = srp_request
        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = {"comment": "Looks good"}

        response = srp_request_approve(
            mock_request, srp_request.srp_link.srp_code, srp_request.request_code
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(json.loads(response.content)["success"], True)
        mock_bulk_create.assert_called_once()
        mock_notify.assert_not_called()

    @patch("aasrp.models.SrpRequest.objects.get")
    def test_returns_error_when_request_does_not_exist(self, mock_get):
        """
        Test that the view returns an error when the SRP request does not exist.

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        mock_request = MagicMock(method="POST")
        mock_get.side_effect = SrpRequest.DoesNotExist

        response = srp_request_approve(
            mock_request, "invalid_srp_code", "invalid_request_code"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "No matching SRP request found"},
        )

    @patch("aasrp.models.SrpRequest.objects.get")
    def test_returns_error_when_request_method_is_not_post(self, mock_get):
        """
        Test that the view returns an error when the request method is not POST.

        :param mock_get:
        :type mock_get:
        :return:
        :rtype:
        """

        srp_request = self.srp_request_pending
        mock_get.return_value = srp_request

        mock_request = MagicMock(method="GET")
        response = srp_request_approve(
            mock_request, "valid_srp_code", "valid_request_code"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid request method"},
        )

    @patch("aasrp.views.ajax.SrpRequestAcceptForm")
    @patch("aasrp.models.SrpRequest.objects.get")
    def test_returns_error_when_approval_form_data_is_invalid(
        self, mock_get, mock_form
    ):
        """
        Test that the view returns an error when the approval form data is invalid.

        :param mock_get:
        :type mock_get:
        :param mock_form:
        :type mock_form:
        :return:
        :rtype:
        """

        srp_request = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            creator=self.user_wesley_crusher,
            request_status=SrpRequest.Status.PENDING,
            loss_amount=100,
            ship=self.ship_test,
        )
        mock_get.return_value = srp_request
        mock_form.return_value.is_valid.return_value = False

        mock_request = MagicMock(method="POST", body=json.dumps({"comment": ""}))
        mock_request.user = self.user_jean_luc_picard

        response = srp_request_approve(
            mock_request, srp_request.srp_link.srp_code, srp_request.request_code
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid form data"},
        )


class TestSrpRequestChangePayout(BaseViewsTestCase):
    """
    Tests for the srp_request_change_payout view.
    """

    def setUp(self):
        """
        Set up the test case by defining the URL for changing payout.

        :return:
        :rtype:
        """

        self.url = reverse(
            "aasrp:ajax_srp_request_change_payout",
            args=[self.srp_link_active.srp_code, self.srp_request_pending.request_code],
        )

    @patch("aasrp.views.ajax.SrpRequestPayoutForm")
    def test_changes_payout_when_form_is_valid(self, mock_form):
        """
        Test that the view changes the payout amount when the form is valid.

        :param mock_form:
        :type mock_form:
        :return:
        :rtype:
        """

        mock_form.return_value.is_valid.return_value = True
        mock_form.return_value.cleaned_data = {"value": 1000}

        self.client.force_login(self.user_jean_luc_picard)

        response = self.client.post(self.url, {"value": 1000})

        self.srp_request_pending.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"success": True})
        self.assertEqual(self.srp_request_pending.payout_amount, 1000)

    @patch("aasrp.views.ajax.SrpRequestPayoutForm")
    def test_returns_failure_when_form_is_invalid(self, mock_form):
        """
        Test that the view returns failure when the form is invalid.

        :param mock_form:
        :type mock_form:
        :return:
        :rtype:
        """

        mock_form.return_value.is_valid.return_value = False

        self.client.force_login(self.user_jean_luc_picard)

        response = self.client.post(self.url, {"value": 1000})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"success": False})

    def test_returns_failure_when_request_does_not_exist(self):
        """
        Test that the view returns failure when the SRP request does not exist.

        :return:
        :rtype:
        """

        url = reverse(
            "aasrp:ajax_srp_request_change_payout",
            args=[self.srp_link_active.srp_code, "invalid_request_code"],
        )

        self.client.force_login(self.user_jean_luc_picard)

        response = self.client.post(url, {"value": 1000})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"success": False})

    def test_returns_failure_when_method_is_not_post(self):
        """
        Test that the view returns failure when the request method is not POST.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_jean_luc_picard)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {"success": False})


class TestSrpRequestAdditionalInformation(BaseViewsTestCase):
    @patch("aasrp.views.ajax.get_formatted_character_name")
    @patch("aasrp.views.ajax.get_type_render_url_from_type_id")
    def test_retrieves_additional_information_for_valid_request(
        self, mock_get_type_render_url, mock_get_formatted_character_name
    ):
        """
        Test that the view retrieves additional information for a valid SRP request.

        :param mock_get_type_render_url:
        :type mock_get_type_render_url:
        :param mock_get_formatted_character_name:
        :type mock_get_formatted_character_name:
        :return:
        :rtype:
        """

        srp_request = SrpRequest.objects.create(
            srp_link=self.srp_link_active,
            request_code="valid_code",
            ship=self.ship_test,
            request_status=SrpRequest.Status.PENDING,
        )
        RequestComment.objects.create(
            srp_request=srp_request,
            comment="Additional info",
            comment_type=RequestComment.Type.REQUEST_INFO,
        )
        mock_get_formatted_character_name.return_value = "Formatted Character"
        mock_get_type_render_url.return_value = "<img src='ship.png'>"

        self.client.force_login(self.user_jean_luc_picard)

        response = self.client.get(
            reverse(
                "aasrp:ajax_srp_request_additional_information",
                args=[self.srp_link_active.srp_code, "valid_code"],
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Test Ship")
        self.assertContains(response, "Formatted Character")
        self.assertContains(response, "Additional info")

    def test_returns_404_for_nonexistent_request(self):
        """
        Test that the view returns a 404 status code for a nonexistent SRP request.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_jean_luc_picard)

        response = self.client.get(
            reverse(
                "aasrp:ajax_srp_request_additional_information",
                args=["invalid_code", "invalid_code"],
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestSrpLinkUpdateTotalCost(BaseViewsTestCase):
    """
    Tests for the srp_link_update_total_cost view.
    """

    def test_returns_success_and_updates_total_cost_for_existing_srp_link(self):
        """
        Test that the view returns success and updates the total cost for an existing SRP link.

        :return:
        """

        request = MagicMock(method="POST", body=json.dumps({"total_cost": 987654321}))

        response = srp_link_update_total_cost(request, self.srp_link_active.srp_code)
        self.srp_link_active.refresh_from_db()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": True, "message": "Total cost updated successfully"},
        )
        self.assertEqual(self.srp_link_active.total_cost, 987654321)

    def test_returns_success_and_allows_zero_total_cost(self):
        """
        Test that the view returns success and allows setting the total cost to zero.

        :return:
        """

        self.srp_link_active.total_cost = 42
        self.srp_link_active.save()

        request = MagicMock(method="POST", body=json.dumps({"total_cost": 0}))

        response = srp_link_update_total_cost(request, self.srp_link_active.srp_code)
        self.srp_link_active.refresh_from_db()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": True, "message": "Total cost updated successfully"},
        )
        self.assertEqual(self.srp_link_active.total_cost, 0)

    def test_returns_error_when_srp_link_does_not_exist(self):
        """
        Test that the view returns an error when the SRP link does not exist.

        :return:
        """

        request = MagicMock(method="POST", body=json.dumps({"total_cost": 500}))

        response = srp_link_update_total_cost(request, "unknown_srp_code")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "SRP link not found"},
        )

    def test_returns_error_for_non_post_requests(self):
        """
        Test that the view returns an error for non-POST requests.

        :return:
        """

        request = MagicMock(method="GET")

        response = srp_link_update_total_cost(request, self.srp_link_active.srp_code)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            json.loads(response.content),
            {"success": False, "message": "Invalid request method"},
        )
