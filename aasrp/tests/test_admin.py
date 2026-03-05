"""
Unit tests for the admin classes in the aasrp application.
"""

# Standard Library
from types import SimpleNamespace
from unittest import mock

# Third Party
from eve_sde.models import ItemType

# Django
from django.contrib.auth.models import User

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# AA SRP
from aasrp.admin import (
    FleetTypeAdmin,
    RequestCommentAdmin,
    SrpLinkAdmin,
    SrpRequestAdmin,
)
from aasrp.models import FleetType, RequestComment, SrpLink, SrpRequest
from aasrp.tests import BaseTestCase


class TestSrpLinkAdmin(BaseTestCase):
    """
    Test case for the SrpLinkAdmin class, which is responsible for displaying SRP links in the Django admin interface.
    """

    def setUp(self):
        """
        Set up the test environment

        :return:
        :rtype:
        """

        self.user = User.objects.create(username="testuser")
        self.srp_link = SrpLink.objects.create(
            srp_code="SRP123",
            srp_name="Test SRP",
            fleet_time="2023-01-01 12:00:00",
            creator=self.user,
            srp_status="Pending",
            fleet_doctrine="Doctrine A",
        )

    def test_displays_correct_creator_name(self):
        """
        Tests that the _creator method returns the correct username for the creator of the SRP link.

        :return:
        :rtype:
        """

        creator_name = SrpLinkAdmin._creator(self.srp_link)

        self.assertEqual(creator_name, "testuser")

    def test_handles_missing_creator(self):
        """
        Tests that the _creator method returns "deleted" when the creator of the SRP link has been deleted.

        :return:
        :rtype:
        """

        self.srp_link.creator = None
        self.srp_link.save()

        creator_name = SrpLinkAdmin._creator(self.srp_link)

        self.assertEqual(creator_name, "deleted")


class TestSrpRequestAdminTests(BaseTestCase):
    """
    Test case for the SrpRequestAdmin class, which is responsible for displaying SRP requests in the Django admin interface.
    """

    def setUp(self):
        """
        Set up the test environment

        :return:
        :rtype:
        """

        self.user = User.objects.create(username="testuser")
        self.srp_link = SrpLink.objects.create(
            srp_code="SRP123",
            srp_name="Test SRP",
            fleet_time="2023-01-01 12:00:00",
            creator=self.user,
            srp_status="Pending",
            fleet_doctrine="Doctrine A",
        )

        self.ship = ItemType.objects.create(name="Test Ship", id=12345)
        self.srp_request = SrpRequest.objects.create(
            request_code="REQ001",
            creator=self.user,
            character=None,
            srp_link=self.srp_link,
            ship=self.ship,
            loss_amount=1000000,
            payout_amount=500000,
            request_status="Pending",
        )

    def test_handles_missing_requestor(self):
        """
        Tests that the _requestor method returns "deleted" when the creator of the SRP request has been deleted.

        :return:
        :rtype:
        """

        self.srp_request.creator = None
        self.srp_request.save()

        requestor_name = SrpRequestAdmin._requestor(self.srp_request)

        self.assertEqual(requestor_name, "deleted")

    def test_displays_correct_srp_code(self):
        """
        Tests that the _srp_code method returns the correct SRP code for the associated SRP link.

        :return:
        :rtype:
        """

        srp_code = SrpRequestAdmin._srp_code(None, self.srp_request)

        self.assertEqual(srp_code, "SRP123")

    def test_displays_correct_ship_name(self):
        """
        Tests that the _ship_name method returns the correct ship name for the associated ship.

        :return:
        :rtype:
        """

        ship_name = SrpRequestAdmin._ship_name(None, self.srp_request)

        self.assertEqual(ship_name, "Test Ship")

    def test_handles_missing_ship(self):
        """
        Tests that the _ship_name method returns "N/A" when the associated ship has been deleted.

        :return:
        :rtype:
        """

        self.srp_request.ship = None
        self.srp_request.save()

        ship_name = SrpRequestAdmin._ship_name(None, self.srp_request)

        self.assertEqual(ship_name, "N/A")

    def test_formats_loss_amount_correctly(self):
        """
        Tests that the _loss_amount method returns the loss amount formatted as a string with two decimal places and a comma as a thousands separator.

        :return:
        :rtype:
        """

        loss_amount = SrpRequestAdmin._loss_amount(None, self.srp_request)

        self.assertEqual(loss_amount, "1,000,000.00 ISK")

    def test_formats_payout_amount_correctly(self):
        """
        Tests that the _payout_amount method returns the payout amount formatted as a string with two decimal places and a comma as a thousands separator.

        :return:
        :rtype:
        """

        payout_amount = SrpRequestAdmin._payout_amount(None, self.srp_request)

        self.assertEqual(payout_amount, "500,000.00 ISK")


class TestRequestCommentAdmin(BaseTestCase):
    """
    Test case for the RequestCommentAdmin class, which is responsible for displaying request comments in the Django admin interface.
    """

    def setUp(self):
        """
        Set up the test environment

        :return:
        :rtype:
        """

        self.user = User.objects.create(username="testuser")
        self.srp_link = SrpLink.objects.create(
            srp_code="SRP123",
            srp_name="Test SRP",
            fleet_time="2023-01-01 12:00:00",
            creator=self.user,
            srp_status="Pending",
            fleet_doctrine="Doctrine A",
        )
        self.srp_request = SrpRequest.objects.create(
            request_code="REQ001",
            creator=self.user,
            character=None,
            srp_link=self.srp_link,
            ship=None,
            loss_amount=1000000,
            payout_amount=500000,
            request_status="Pending",
        )
        self.comment = RequestComment.objects.create(
            srp_request=self.srp_request,
            comment_type="General",
        )

    def test_displays_correct_srp_code(self):
        """
        Tests that the _srp_code method returns the correct SRP code for the associated SRP link.

        :return:
        :rtype:
        """

        srp_code = RequestCommentAdmin._srp_code(None, self.comment)

        self.assertEqual(srp_code, "SRP123")

    def test_displays_correct_request_code(self):
        """
        Tests that the _request_code method returns the correct request code for the associated SRP request.

        :return:
        :rtype:
        """

        request_code = RequestCommentAdmin._request_code(None, self.comment)

        self.assertEqual(request_code, "REQ001")

    def test_displays_correct_requestor_name(self):
        """
        Tests that the _requestor method returns the correct username for the creator of the SRP request.

        :return:
        :rtype:
        """

        requestor_name = RequestCommentAdmin._requestor(None, self.comment)

        self.assertEqual(requestor_name, "testuser")

    def test_handles_missing_requestor(self):
        """
        Tests that the _requestor method returns "deleted" when the creator of the SRP request has been deleted.

        :return:
        :rtype:
        """

        self.srp_request.creator = None
        self.srp_request.save()

        requestor_name = RequestCommentAdmin._requestor(None, self.comment)

        self.assertEqual(requestor_name, "deleted")

    def test_displays_correct_character_name(self):
        """
        Tests that the _character method returns the correct character name for the associated character.

        :return:
        :rtype:
        """

        char = EveCharacter(character_name="TestChar")
        self.srp_request.character = char

        character_name = RequestCommentAdmin._character(None, self.comment)

        self.assertEqual(character_name, "TestChar")


class TestFleetTypeAdmin(BaseTestCase):
    """
    Test case for the FleetTypeAdmin class, which is responsible for displaying fleet types in the Django admin interface.
    """

    def test_activates_selected_fleet_types(self):
        """
        Tests that the activate method sets is_enabled to True for all selected fleet types.

        :return:
        :rtype:
        """

        fleet_type_1 = FleetType.objects.create(name="Fleet A", is_enabled=False)
        fleet_type_2 = FleetType.objects.create(name="Fleet B", is_enabled=False)
        queryset = FleetType.objects.filter(id__in=[fleet_type_1.id, fleet_type_2.id])
        request = SimpleNamespace()

        with (
            mock.patch("aasrp.admin.messages.success"),
            mock.patch("aasrp.admin.messages.error"),
        ):
            FleetTypeAdmin.activate(None, request, queryset)

        fleet_type_1.refresh_from_db()
        fleet_type_2.refresh_from_db()

        self.assertTrue(fleet_type_1.is_enabled)
        self.assertTrue(fleet_type_2.is_enabled)

    def test_handles_activation_failure_gracefully(self):
        """
        Tests that the activate method handles exceptions gracefully and does not change the is_enabled status if an error occurs.

        :return:
        :rtype:
        """

        fleet_type = FleetType.objects.create(name="Fleet C", is_enabled=False)
        queryset = FleetType.objects.filter(id=fleet_type.id)
        request = SimpleNamespace()

        with (
            mock.patch.object(FleetType, "save", side_effect=Exception("Save failed")),
            mock.patch("aasrp.admin.messages.success"),
            mock.patch("aasrp.admin.messages.error"),
        ):
            FleetTypeAdmin.activate(None, request, queryset)

        fleet_type.refresh_from_db()

        self.assertFalse(fleet_type.is_enabled)

    def test_deactivates_selected_fleet_types(self):
        """
        Tests that the deactivate method sets is_enabled to False for all selected fleet types.

        :return:
        :rtype:
        """

        fleet_type_1 = FleetType.objects.create(name="Fleet D", is_enabled=True)
        fleet_type_2 = FleetType.objects.create(name="Fleet E", is_enabled=True)
        queryset = FleetType.objects.filter(id__in=[fleet_type_1.id, fleet_type_2.id])
        request = SimpleNamespace()

        with (
            mock.patch("aasrp.admin.messages.success"),
            mock.patch("aasrp.admin.messages.error"),
        ):
            FleetTypeAdmin.deactivate(None, request, queryset)

        fleet_type_1.refresh_from_db()
        fleet_type_2.refresh_from_db()

        self.assertFalse(fleet_type_1.is_enabled)
        self.assertFalse(fleet_type_2.is_enabled)

    def test_handles_deactivation_failure_gracefully(self):
        """
        Tests that the deactivate method handles exceptions gracefully and does not change the is_enabled status if an error occurs.

        :return:
        :rtype:
        """

        fleet_type = FleetType.objects.create(name="Fleet F", is_enabled=True)
        queryset = FleetType.objects.filter(id=fleet_type.id)
        request = SimpleNamespace()

        with (
            mock.patch.object(FleetType, "save", side_effect=Exception("Save failed")),
            mock.patch("aasrp.admin.messages.success"),
            mock.patch("aasrp.admin.messages.error"),
        ):
            FleetTypeAdmin.deactivate(None, request, queryset)

        fleet_type.refresh_from_db()

        self.assertTrue(fleet_type.is_enabled)
