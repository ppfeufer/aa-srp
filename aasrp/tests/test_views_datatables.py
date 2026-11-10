"""
Unit tests for the OwnSrpRequestsView datatable view.
"""

# Standard Library
from unittest.mock import MagicMock

# Third Party
from eve_sde.models import ItemType

# Django
from django.core.exceptions import PermissionDenied
from django.http import QueryDict
from django.utils import timezone

# AA SRP
from aasrp.models import SrpLink, SrpRequest
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_fake_user, random_id
from aasrp.views.datatables import dashboard, view_own_requests


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

        self.user = create_fake_user(
            character_id=random_id(),
            character_name="Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )
        self.view = view_own_requests.OwnSrpRequestsView()
        self.request = MagicMock(user=self.user)
        self.srp_link = SrpLink.objects.create(
            srp_code="TEST001", creator=self.user, fleet_time=timezone.now()
        )

    def test_returns_queryset_filtered_by_request_status(self):
        """
        Test that the view returns a queryset filtered by request status.

        :return:
        """

        SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.APPROVED,
            srp_link=self.srp_link,
        )
        SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.PENDING,
            srp_link=self.srp_link,
        )
        self.request.GET = QueryDict(
            f"dropdown_filter[request_status]={SrpRequest.Status.APPROVED}"
        )
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().request_status, SrpRequest.Status.APPROVED)

    def test_returns_queryset_filtered_by_character(self):
        """
        Test that the view returns a queryset filtered by character.

        :return:
        """

        # Alliance Auth
        from allianceauth.eveonline.models import EveCharacter

        character = EveCharacter.objects.create(
            character_id=random_id(),
            character_name="Test Character",
            corporation_id=1,
            corporation_name="Test Corp",
        )
        SrpRequest.objects.create(
            creator=self.user, character=character, srp_link=self.srp_link
        )
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        self.request.GET = QueryDict(
            f"dropdown_filter[character]={character.character_id}"
        )
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(
            queryset.first().character.character_id, character.character_id
        )

    def test_returns_queryset_filtered_by_ship(self):
        """
        Test that the view returns a queryset filtered by ship.

        :return:
        """

        ship = ItemType.objects.create(pk=12345, name="TestShip")
        SrpRequest.objects.create(creator=self.user, ship=ship, srp_link=self.srp_link)
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)

        self.request.GET = QueryDict(f"dropdown_filter[ship]={ship.pk}")

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().ship.pk, ship.pk)

    def test_returns_full_queryset_when_no_filters_applied(self):
        """
        Test that the view returns the full queryset when no filters are applied.

        :return:
        """

        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)

        self.request.GET = QueryDict()

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 2)

    def test_returns_empty_queryset_for_non_matching_filters(self):
        """
        Test that the view returns an empty queryset when filters do not match any records.

        :return:
        """

        SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.APPROVED,
            srp_link=self.srp_link,
        )
        self.request.GET = QueryDict(
            f"dropdown_filter[request_status]={SrpRequest.Status.PENDING}"
        )

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 0)


class TestDashboardSrpLinksView(BaseTestCase):
    """
    Test case for DashboardSrpLinksView datatable view.
    """

    def setUp(self):
        """
        Set up test data for DashboardSrpLinksView tests.

        :return:
        """

        self.user = create_fake_user(
            character_id=random_id(),
            character_name="Kathryn Janeway",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )
        self.view = dashboard.DashboardSrpLinksView()
        self.request = MagicMock(user=self.user, GET=QueryDict())

    def test_returns_only_active_links_by_default(self):
        """
        Test that the view returns only active SRP links by default.

        :return:
        """

        active_link = SrpLink.objects.create(
            srp_code="ACTIVE001", creator=self.user, fleet_time=timezone.now()
        )
        SrpLink.objects.create(
            srp_code="CLOSED001",
            creator=self.user,
            fleet_time=timezone.now(),
            srp_status=SrpLink.Status.CLOSED,
        )

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, active_link.id)

    def test_basic_user_sees_only_active_links_by_default(self):
        basic_user = create_fake_user(
            character_id=random_id(),
            character_name="Basic User",
            permissions=["aasrp.basic_access"],
        )
        self.request.user = basic_user
        active_link = SrpLink.objects.create(
            srp_code="BASICACTIVE", creator=self.user, fleet_time=timezone.now()
        )
        SrpLink.objects.create(
            srp_code="BASICCLOSED",
            creator=self.user,
            fleet_time=timezone.now(),
            srp_status=SrpLink.Status.CLOSED,
        )

        self.assertSetEqual(
            set(self.view.get_model_qs(self.request).values_list("id", flat=True)),
            {active_link.id},
        )

    def test_returns_all_links_when_show_all_links_is_enabled(self):
        """
        Test that the view returns all SRP links when show_all_links is enabled.

        :return:
        """

        self.view.show_all_links = True

        active_link = SrpLink.objects.create(
            srp_code="ACTIVE002", creator=self.user, fleet_time=timezone.now()
        )
        closed_link = SrpLink.objects.create(
            srp_code="CLOSED002",
            creator=self.user,
            fleet_time=timezone.now(),
            srp_status=SrpLink.Status.CLOSED,
        )

        queryset = self.view.get_model_qs(self.request)

        self.assertSetEqual(
            set(queryset.values_list("id", flat=True)), {active_link.id, closed_link.id}
        )

    def test_basic_user_cannot_view_all_links(self):
        """
        Test that a basic user cannot view all SRP links when show_all_links is enabled.

        :return:
        """

        self.request.user = create_fake_user(
            character_id=random_id(),
            character_name="Basic User",
            permissions=["aasrp.basic_access"],
        )
        self.view.show_all_links = True

        with self.assertRaises(PermissionDenied):
            self.view.get_model_qs(self.request)

    def test_returns_only_links_with_pending_requests_when_has_requests_filter_is_true(
        self,
    ):
        """
        Test that the view returns only SRP links with pending requests when the

        :return:
        """

        link_with_pending = SrpLink.objects.create(
            srp_code="PENDING001", creator=self.user, fleet_time=timezone.now()
        )
        link_with_approved_only = SrpLink.objects.create(
            srp_code="APPROVED001", creator=self.user, fleet_time=timezone.now()
        )
        SrpLink.objects.create(
            srp_code="NONE001", creator=self.user, fleet_time=timezone.now()
        )
        SrpRequest.objects.create(
            creator=self.user,
            srp_link=link_with_pending,
            request_status=SrpRequest.Status.PENDING,
        )
        SrpRequest.objects.create(
            creator=self.user,
            srp_link=link_with_approved_only,
            request_status=SrpRequest.Status.APPROVED,
        )
        self.request.GET = QueryDict("filter[has_requests]=true")

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, link_with_pending.id)

    def test_treats_has_requests_filter_as_case_insensitive(self):
        """
        Test that the view treats the has_requests filter as case-insensitive.

        :return:
        """

        link_with_pending = SrpLink.objects.create(
            srp_code="PENDING002", creator=self.user, fleet_time=timezone.now()
        )
        SrpRequest.objects.create(
            creator=self.user,
            srp_link=link_with_pending,
            request_status=SrpRequest.Status.PENDING,
        )
        self.request.GET = QueryDict("filter[has_requests]=TRUE")

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, link_with_pending.id)

    def test_ignores_has_requests_filter_for_non_true_values(self):
        """
        Test that the view ignores the has_requests filter for non-true values.

        :return:
        """

        active_link = SrpLink.objects.create(
            srp_code="ACTIVE003", creator=self.user, fleet_time=timezone.now()
        )
        SrpLink.objects.create(
            srp_code="ACTIVE004", creator=self.user, fleet_time=timezone.now()
        )
        self.request.GET = QueryDict("filter[has_requests]=1")

        queryset = self.view.get_model_qs(self.request)

        self.assertEqual(queryset.count(), 2)
        self.assertIn(active_link.id, queryset.values_list("id", flat=True))
