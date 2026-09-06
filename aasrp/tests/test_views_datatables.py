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
from aasrp.tests.utils import create_fake_user, random_id
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
            character_id=random_id(),
            character_name="Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )
        self.view = OwnSrpRequestsView()
        self.request = MagicMock(user=self.user)
        self.srp_link = SrpLink.objects.create(
            srp_code="TEST001", creator=self.user, fleet_time=timezone.now()
        )

    def test_returns_queryset_filtered_by_request_status(self):
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
        ship = ItemType.objects.create(pk=12345, name="TestShip")
        SrpRequest.objects.create(creator=self.user, ship=ship, srp_link=self.srp_link)
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        self.request.GET = QueryDict(f"dropdown_filter[ship]={ship.pk}")
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().ship.pk, ship.pk)

    def test_returns_full_queryset_when_no_filters_applied(self):
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        SrpRequest.objects.create(creator=self.user, srp_link=self.srp_link)
        self.request.GET = QueryDict()
        queryset = self.view.get_model_qs(self.request)
        self.assertEqual(queryset.count(), 2)

    def test_returns_empty_queryset_for_non_matching_filters(self):
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
