"""
Unit tests for the OwnSrpRequestsView datatable view.
"""

# Standard Library
from unittest.mock import MagicMock

# Django
from django.contrib.auth.models import User
from django.utils import timezone

# AA SRP
from aasrp.models import SrpLink, SrpRequest
from aasrp.tests import BaseTestCase
from aasrp.views.datatables import OwnSrpRequestsView


class TestOwnSrpRequestsView(BaseTestCase):
    """
    Test case for OwnSrpRequestsView datatable view.
    """

    def setUp(self):
        """
        Set up test data for OwnSrpRequestsView tests.

        :return:
        :rtype:
        """

        self.user = User.objects.create_user(username="testuser", password="password")
        self.view = OwnSrpRequestsView()
        self.request = MagicMock(user=self.user)
        self.srp_link = SrpLink.objects.create(
            srp_code="TEST001", creator=self.user, fleet_time=timezone.now()
        )

    def test_retrieves_only_requests_created_by_user(self):
        """
        Test that get_model_qs retrieves only SrpRequest objects created by the user.

        :return:
        :rtype:
        """

        SrpRequest.objects.create(
            creator=self.user, request_code="REQ001", srp_link=self.srp_link
        )
        SrpRequest.objects.create(
            creator=self.user, request_code="REQ002", srp_link=self.srp_link
        )
        SrpRequest.objects.create(
            creator=User.objects.create_user(username="otheruser"),
            request_code="REQ003",
            srp_link=self.srp_link,
        )

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 2)
        self.assertTrue(all(req.creator == self.user for req in queryset))

    def test_handles_empty_queryset(self):
        """
        Test that get_model_qs handles an empty queryset correctly.

        :return:
        :rtype:
        """

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 0)

    def test_prefetches_related_fields(self):
        """
        Test that get_model_qs prefetches related fields to optimize database queries.

        :return:
        :rtype:
        """

        SrpRequest.objects.create(
            creator=self.user, request_code="REQ001", srp_link=self.srp_link
        )

        queryset = self.view.get_model_qs(self.request)

        self.assertTrue(len(queryset._prefetch_related_lookups) > 0)
