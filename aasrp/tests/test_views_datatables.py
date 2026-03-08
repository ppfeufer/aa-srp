"""
Unit tests for the OwnSrpRequestsView datatable view.
"""

# Standard Library
from unittest.mock import MagicMock

# Third Party
from eve_sde.models import ItemType

# Django
from django.http import QueryDict
from django.utils import timezone

# AA SRP
from aasrp.models import SrpLink, SrpRequest
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_fake_user
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

        self.user = create_fake_user(
            character_id=1000,
            character_name="Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )
        self.view = OwnSrpRequestsView()
        self.request = MagicMock(user=self.user)
        self.srp_link = SrpLink.objects.create(
            srp_code="TEST001", creator=self.user, fleet_time=timezone.now()
        )

    # def test_retrieves_only_requests_created_by_user(self):
    #     """
    #     Test that get_model_qs retrieves only SrpRequest objects created by the user.
    #
    #     :return:
    #     :rtype:
    #     """
    #
    #     SrpRequest.objects.create(
    #         creator=self.user, request_code="REQ001", srp_link=self.srp_link
    #     )
    #     SrpRequest.objects.create(
    #         creator=self.user, request_code="REQ002", srp_link=self.srp_link
    #     )
    #     SrpRequest.objects.create(
    #         creator=User.objects.create_user(username="otheruser"),
    #         request_code="REQ003",
    #         srp_link=self.srp_link,
    #     )
    #
    #     queryset = self.view.get_model_qs(self.request)
    #
    #     self.assertEqual(queryset.count(), 2)
    #     self.assertTrue(all(req.creator == self.user for req in queryset))

    # def test_handles_empty_queryset(self):
    #     """
    #     Test that get_model_qs handles an empty queryset correctly.
    #
    #     :return:
    #     :rtype:
    #     """
    #
    #     queryset = self.view.get_model_qs(self.request)
    #
    #     self.assertEqual(queryset.count(), 0)

    # def test_prefetches_related_fields(self):
    #     """
    #     Test that get_model_qs prefetches related fields to optimize database queries.
    #
    #     :return:
    #     :rtype:
    #     """
    #
    #     SrpRequest.objects.create(
    #         creator=self.user, request_code="REQ001", srp_link=self.srp_link
    #     )
    #
    #     queryset = self.view.get_model_qs(self.request)
    #
    #     self.assertTrue(len(queryset._prefetch_related_lookups) > 0)

    def test_returns_queryset_filtered_by_request_status(self):
        SrpRequest.objects.create(
            creator=self.user, request_status="approved", srp_link=self.srp_link
        )
        SrpRequest.objects.create(
            creator=self.user, request_status="pending", srp_link=self.srp_link
        )
        self.request.GET = QueryDict("filter_request_status=approved")
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().request_status, "approved")

    def test_returns_queryset_filtered_by_character(self):
        # Alliance Auth
        from allianceauth.eveonline.models import EveCharacter

        character = EveCharacter.objects.create(
            character_id=12345,
            character_name="Test Character",
            corporation_id=1,
            corporation_name="Test Corp",
        )
        SrpRequest.objects.create(
            creator=self.user, character=character, srp_link=self.srp_link
        )
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        self.request.GET = QueryDict(f"filter_character={character.character_id}")
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(
            queryset.first().character.character_id, character.character_id
        )

    def test_returns_queryset_filtered_by_ship(self):
        ship = ItemType.objects.create(id=12345, name="TestShip")
        SrpRequest.objects.create(creator=self.user, ship=ship, srp_link=self.srp_link)
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        self.request.GET = QueryDict(f"filter_ship={ship.id}")
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().ship.id, ship.id)

    def test_returns_full_queryset_when_no_filters_applied(self):
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        self.request.GET = QueryDict()
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 2)

    def test_returns_empty_queryset_for_non_matching_filters(self):
        SrpRequest.objects.create(
            creator=self.user, request_status="approved", srp_link=self.srp_link
        )
        self.request.GET = QueryDict("filter_request_status=pending")
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 0)
