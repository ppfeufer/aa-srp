"""
Unit tests for the SrpRequest model in the AA SRP application.
"""

# Standard Library
from unittest.mock import MagicMock, patch

# Third Party
from eve_sde.models import ItemType

# Django
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

# Alliance Auth
from allianceauth.groupmanagement.models import Group

# AA SRP
from aasrp.models import BonusGroup, SrpLink, SrpRequest
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_eve_character, create_fake_user, random_id


class TestSrpRequest(BaseTestCase):
    """
    Test case for the SrpRequest model.
    """

    def setUp(self):
        """
        Setup a mock SrpRequest instance for testing.

        :return:
        :rtype:
        """

        self.user = create_fake_user(
            character_id=random_id(),
            character_name="Willam Riker",
            corporation_id=98000001,
            corporation_name="Bridge Vrew",
            corporation_ticker="BC",
            alliance_id=99000001,
            alliance_name="USS Enterprise",
            alliance_ticker="NX-01",
        )
        self.character = self.user.profile.main_character

        self.character_2 = create_eve_character(
            character_id=random_id(),
            character_name="Worf",
            corporation_id=98000001,
            corporation_name="Bridge Crew",
            corporation_ticker="BC",
        )
        # minimal ItemType/Ship entry
        self.ship_type = ItemType.objects.create(
            id=587, name="Test Ship", published=True
        )
        self.srp_link_1 = SrpLink.objects.create(
            srp_name="Test SRP", fleet_time=timezone.now()
        )

        # keep mocks for tests that exercise __str__ and permission logic
        self.srp_request = MagicMock(spec=SrpRequest)
        self.srp_request.character = MagicMock()
        self.srp_request.character.character_name = "Test Character"
        self.srp_request.creator = MagicMock()
        self.srp_request.ship = MagicMock()
        self.srp_request.ship.name = "Test Ship"
        self.srp_request.request_code = "REQ123"

    @patch("aasrp.models.get_main_character_name_from_user")
    def test_returns_correct_string_representation(self, mock_get_main_character_name):
        """
        Test that the string representation of an SrpRequest instance is correct.

        :param mock_get_main_character_name:
        :type mock_get_main_character_name:
        :return:
        :rtype:
        """

        mock_get_main_character_name.return_value = "Main Character"
        result = SrpRequest.__str__(self.srp_request)

        self.assertEqual(
            result,
            "Test Character (Main Character) SRP request for: Test Ship (REQ123)",
        )

    @patch("aasrp.models.get_main_character_name_from_user")
    def test_handles_missing_character_name(self, mock_get_main_character_name):
        """
        Test that the string representation handles a missing character name.

        :param mock_get_main_character_name:
        :type mock_get_main_character_name:
        :return:
        :rtype:
        """

        self.srp_request.character.character_name = None
        self.srp_request.ship = MagicMock()
        self.srp_request.ship.name = "Test Ship"
        mock_get_main_character_name.return_value = "Main Character"

        result = SrpRequest.__str__(self.srp_request)

        self.assertEqual(
            result, "None (Main Character) SRP request for: Test Ship (REQ123)"
        )

    @patch("aasrp.models.get_main_character_name_from_user")
    def test_handles_missing_creator(self, mock_get_main_character_name):
        """
        Test that the string representation handles a missing creator.

        :param mock_get_main_character_name:
        :type mock_get_main_character_name:
        :return:
        :rtype:
        """

        self.srp_request.creator = None
        self.srp_request.ship = MagicMock()
        self.srp_request.ship.name = "Test Ship"
        mock_get_main_character_name.return_value = None

        result = SrpRequest.__str__(self.srp_request)

        self.assertEqual(
            result, "Test Character (None) SRP request for: Test Ship (REQ123)"
        )

    @patch("aasrp.models.get_main_character_name_from_user")
    def test_handles_missing_ship_name(self, mock_get_main_character_name):
        """
        Test that the string representation handles a missing ship name.

        :param mock_get_main_character_name:
        :type mock_get_main_character_name:
        :return:
        :rtype:
        """

        self.srp_request.ship.name = None

        mock_get_main_character_name.return_value = "Main Character"
        result = SrpRequest.__str__(self.srp_request)

        self.assertEqual(
            result, "Test Character (Main Character) SRP request for: None (REQ123)"
        )

    @patch("aasrp.models.get_main_character_name_from_user")
    def test_handles_missing_request_code(self, mock_get_main_character_name):
        """
        Test that the string representation handles a missing request code.

        :param mock_get_main_character_name:
        :type mock_get_main_character_name:
        :return:
        :rtype:
        """

        self.srp_request.request_code = None
        self.srp_request.ship = MagicMock()
        self.srp_request.ship.name = "Test Ship"

        mock_get_main_character_name.return_value = "Main Character"
        result = SrpRequest.__str__(self.srp_request)

        self.assertEqual(
            result, "Test Character (Main Character) SRP request for: Test Ship (None)"
        )

    @patch("aasrp.models.SrpRequest.objects.filter")
    def test_returns_pending_requests_count_for_user_with_permission(self, mock_filter):
        user = MagicMock()
        user.has_perm.side_effect = lambda perm: perm in ["aasrp.manage_srp"]
        mock_filter.return_value.count.return_value = 5

        result = SrpRequest.pending_requests_count_for_user(user)

        self.assertEqual(result, 5)
        user.has_perm.assert_called_with(perm="aasrp.manage_srp")
        mock_filter.assert_called_with(request_status=SrpRequest.Status.PENDING)

    @patch("aasrp.models.SrpRequest.objects.filter")
    def test_returns_none_for_user_without_permission(self, mock_filter):
        user = MagicMock()
        user.has_perm.return_value = False

        result = SrpRequest.pending_requests_count_for_user(user)

        self.assertIsNone(result)
        user.has_perm.assert_called_with(perm="aasrp.manage_srp_requests")
        mock_filter.assert_not_called()

    @patch("aasrp.models.SrpRequest.objects.filter")
    def test_returns_none_for_anonymous_user(self, mock_filter):
        user = AnonymousUser()

        result = SrpRequest.pending_requests_count_for_user(user)

        self.assertIsNone(result)
        mock_filter.assert_not_called()

    def test_saves_request_with_empty_code_generates_unique_code(self):
        """
        Test that saving an SrpRequest with an empty request_code generates a unique code.

        :return:
        :rtype:
        """

        srp_request = SrpRequest(
            creator=self.user,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
            request_code="",
        )
        srp_request.save()

        self.assertNotEqual(srp_request.request_code, "")
        self.assertEqual(len(srp_request.request_code), 16)

    def test_saves_request_with_existing_code_preserves_code(self):
        """
        Test that saving an SrpRequest with an existing request_code preserves the code.

        :return:
        :rtype:
        """

        srp_request = SrpRequest(
            creator=self.user,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
            request_code="EXISTINGCODE1234",
        )
        srp_request.save()

        self.assertEqual(srp_request.request_code, "EXISTINGCODE1234")

    def test_saves_request_with_empty_code_generates_different_codes_for_multiple_requests(
        self,
    ):
        srp_request1 = SrpRequest(
            creator=self.user,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
            request_code="",
        )
        srp_request1.save()

        srp_request2 = SrpRequest(
            creator=self.user,
            character=self.character_2,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
            request_code="",
        )
        srp_request2.save()

        self.assertNotEqual(srp_request1.request_code, srp_request2.request_code)
        self.assertEqual(len(srp_request1.request_code), 16)
        self.assertEqual(len(srp_request2.request_code), 16)

    def test_assigns_bonus_percentage_from_creator_membership(self):
        """
        Test that the bonus percentage is assigned based on the creator's group membership.

        :return:
        """

        group = Group.objects.create(name="Capital Pilots")
        BonusGroup.objects.create(group=group, bonus_percentage=15.0)
        self.user.groups.add(group)

        srp_request = SrpRequest.objects.create(
            creator=self.user,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
        )

        srp_request.refresh_from_db()
        self.assertEqual(srp_request.bonus_srp, 15.0)

    def test_assigns_highest_bonus_percentage_for_multiple_matching_groups(self):
        """
        Test that the highest bonus percentage is assigned when the creator belongs to multiple groups with different bonus percentages.

        :return:
        """

        lower_group = Group.objects.create(name="Logistics Pilots")
        higher_group = Group.objects.create(name="Capital Pilots")
        BonusGroup.objects.create(group=lower_group, bonus_percentage=10.0)
        BonusGroup.objects.create(group=higher_group, bonus_percentage=25.0)
        self.user.groups.add(lower_group, higher_group)

        srp_request = SrpRequest.objects.create(
            creator=self.user,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
        )

        srp_request.refresh_from_db()
        self.assertEqual(srp_request.bonus_srp, 25.0)

    def test_leaves_bonus_percentage_zero_when_creator_has_no_bonus_group(self):
        """
        Test that the bonus percentage remains zero when the creator does not belong to any bonus group.

        :return:
        """

        unrelated_group = Group.objects.create(name="Social Members")
        BonusGroup.objects.create(group=unrelated_group, bonus_percentage=20.0)

        srp_request = SrpRequest.objects.create(
            creator=self.user,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
        )

        srp_request.refresh_from_db()
        self.assertEqual(srp_request.bonus_srp, 0.0)

    def test_leaves_bonus_percentage_zero_when_creator_is_not_set(self):
        """
        Test that the bonus percentage remains zero when the creator is not set.

        :return:
        """

        srp_request = SrpRequest.objects.create(
            creator=None,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
        )

        srp_request.refresh_from_db()
        self.assertEqual(srp_request.bonus_srp, 0.0)

    def test_preserves_existing_bonus_percentage_on_save(self):
        """
        Test that the existing bonus percentage is preserved when saving an SRP request.

        :return:
        """

        group = Group.objects.create(name="Capital Pilots")
        BonusGroup.objects.create(group=group, bonus_percentage=25.0)
        self.user.groups.add(group)

        srp_request = SrpRequest.objects.create(
            creator=self.user,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
            bonus_srp=10.0,
        )
        srp_request.save()

        srp_request.refresh_from_db()
        self.assertEqual(srp_request.bonus_srp, 10.0)

    def test_assigns_default_bonus_when_saved_request_still_has_zero_percentage(self):
        """
        Test that the default bonus percentage is assigned when saving an SRP request with zero percentage.

        :return:
        """

        group = Group.objects.create(name="Capital Pilots")
        BonusGroup.objects.create(group=group, bonus_percentage=12.5)
        self.user.groups.add(group)

        srp_request = SrpRequest.objects.create(
            creator=self.user,
            character=self.character,
            ship=self.ship_type,
            srp_link=self.srp_link_1,
        )

        srp_request.refresh_from_db()
        self.assertEqual(srp_request.bonus_srp, 12.5)
