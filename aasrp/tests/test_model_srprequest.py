# Standard Library
from unittest.mock import MagicMock, patch

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
        self.srp_request.character.character_name = "Test Character"
        self.srp_request.creator = MagicMock()
        self.srp_request.ship_name = "Test Ship"
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

        self.srp_request.ship_name = None

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

        mock_get_main_character_name.return_value = "Main Character"
        result = SrpRequest.__str__(self.srp_request)

        self.assertEqual(
            result, "Test Character (Main Character) SRP request for: Test Ship (None)"
        )
