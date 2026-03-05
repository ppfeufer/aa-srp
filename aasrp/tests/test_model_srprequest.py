# Standard Library
from unittest.mock import MagicMock, patch

# Django
from django.contrib.auth.models import AnonymousUser

# AA SRP
from aasrp.models import SrpRequest
from aasrp.tests import BaseTestCase


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

        self.srp_request = MagicMock(spec=SrpRequest)
        # provide related objects matching the model's usage
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
