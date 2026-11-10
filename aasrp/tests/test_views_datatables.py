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
from aasrp.models import RequestComment, SrpLink, SrpRequest
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_fake_user, random_id
from aasrp.views.datatables import dashboard, view_own_requests, view_requests


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


class TestSrpRequestsView(BaseTestCase):
    """
    Test case for SrpRequestsView datatable view.
    """

    def setUp(self):
        """
        Set up test data for SrpRequestsView tests.

        :return:
        """

        self.user = create_fake_user(
            character_id=random_id(),
            character_name="Benjamin Sisko",
            permissions=["aasrp.manage_srp_requests"],
        )
        self.view = view_requests.SrpRequestsView()
        self.view.request = MagicMock(user=self.user)
        self.request = MagicMock(user=self.user, GET=QueryDict())
        self.srp_link = SrpLink.objects.create(
            srp_code="SRP001", creator=self.user, fleet_time=timezone.now()
        )
        self.other_srp_link = SrpLink.objects.create(
            srp_code="SRP002", creator=self.user, fleet_time=timezone.now()
        )

    def test_has_permission_returns_true_when_user_has_any_required_permission(self):
        """
        Test that has_permission returns True when the user has any of the required permissions.

        :return:
        """

        self.assertTrue(self.view.has_permission())

    def test_has_permission_returns_false_when_user_has_no_required_permissions(self):
        """
        Test that has_permission returns False when the user has none of the required permissions.

        :return:
        """

        self.view.request.user = create_fake_user(
            character_id=random_id(),
            character_name="Nog",
            permissions=["aasrp.basic_access"],
        )

        self.assertFalse(self.view.has_permission())

    def test_has_permission_supports_single_permission_string(self):
        """
        Test that has_permission supports a single permission string instead of a tuple.

        :return:
        """

        self.view.permission_required = "aasrp.manage_srp_requests"

        self.assertTrue(self.view.has_permission())

    def test_has_permission_returns_true_when_get_permission_required_returns_string(
        self,
    ):
        """
        Test that has_permission returns True when get_permission_required returns a string.

        :return:
        """

        self.view.get_permission_required = MagicMock(
            return_value="aasrp.manage_srp_requests"
        )

        self.assertTrue(self.view.has_permission())

    def test_returns_only_requests_for_matching_srp_code_case_insensitive(self):
        """
        Test that the view returns only requests for the matching SRP code, case-insensitive.

        :return:
        """

        matching_request = SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.PENDING,
            srp_link=self.srp_link,
        )
        SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.PENDING,
            srp_link=self.other_srp_link,
        )

        queryset = self.view.get_model_qs(self.request, srp_code="srp001")

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, matching_request.id)

    def test_filters_requests_by_request_status_when_filter_is_provided(self):
        """
        Test that the view filters requests by request status when the filter is provided.

        :return:
        """

        approved_request = SrpRequest.objects.create(
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
            f"filter[request_status]={SrpRequest.Status.APPROVED}"
        )

        queryset = self.view.get_model_qs(self.request, srp_code="SRP001")

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, approved_request.id)

    def test_returns_all_statuses_when_request_status_filter_is_not_provided(self):
        """
        Test that the view returns all request statuses when the request status filter is not provided.

        :return:
        """

        approved_request = SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.APPROVED,
            srp_link=self.srp_link,
        )
        pending_request = SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.PENDING,
            srp_link=self.srp_link,
        )

        queryset = self.view.get_model_qs(self.request, srp_code="SRP001")

        self.assertSetEqual(
            set(queryset.values_list("id", flat=True)),
            {approved_request.id, pending_request.id},
        )

    def test_summary_includes_all_request_counts_and_payout_totals_for_srp_link(self):
        """
        Test that the summary includes every request on the SRP link, regardless
        of the current table page or status filter.
        """

        SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.APPROVED,
            payout_amount=100,
            srp_link=self.srp_link,
        )
        SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.PENDING,
            payout_amount=200,
            srp_link=self.srp_link,
        )
        SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.REJECTED,
            payout_amount=300,
            srp_link=self.srp_link,
        )
        SrpRequest.objects.create(
            creator=self.user,
            request_status=SrpRequest.Status.APPROVED,
            payout_amount=400,
            srp_link=self.other_srp_link,
        )

        summary = self.view._get_summary(srp_code=self.srp_link.srp_code)

        self.assertEqual(
            summary,
            {
                "requestsTotal": 3,
                "requestsPending": 1,
                "requestsApproved": 1,
                "requestsRejected": 1,
                "totalSrpAmount": 100,
                "pendingSrpAmount": 200,
            },
        )

    def test_loads_only_request_information_comments_for_each_request(self):
        """
        Test that the view loads only request information comments for each request.

        :return:
        """

        srp_request = SrpRequest.objects.create(
            creator=self.user, srp_link=self.srp_link
        )
        RequestComment.objects.create(
            srp_request=srp_request,
            creator=self.user,
            comment_type=RequestComment.Type.COMMENT,
            comment="General comment",
        )
        first_info_comment = RequestComment.objects.create(
            srp_request=srp_request,
            creator=self.user,
            comment_type=RequestComment.Type.REQUEST_INFO,
            comment="First info",
        )
        second_info_comment = RequestComment.objects.create(
            srp_request=srp_request,
            creator=self.user,
            comment_type=RequestComment.Type.REQUEST_INFO,
            comment="Second info",
        )

        row = self.view.get_model_qs(self.request, srp_code="SRP001").first()

        self.assertEqual(len(row.request_info_comments), 2)
        self.assertEqual(
            [comment.id for comment in row.request_info_comments],
            [first_info_comment.id, second_info_comment.id],
        )
