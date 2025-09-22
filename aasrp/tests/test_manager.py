"""
Unit tests for the SrpRequestManager class.
"""

# Standard Library
from unittest.mock import MagicMock, patch

# AA SRP
from aasrp.managers import SrpRequestManager
from aasrp.tests import BaseTestCase


class TestSrpRequestManagerGetZkillboardData(BaseTestCase):
    """
    Test cases for SrpRequestManager.get_zkillboard_data method.
    """

    def test_returns_killmail_data_when_valid_response(self):
        """
        Test that get_zkillboard_data returns correct data when a valid response is received.

        :return:
        :rtype:
        """

        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"killmail_id": 12345, "zkb": {"hash": "abc123"}}
        ]
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            result = SrpRequestManager.get_zkillboard_data("12345")

            self.assertEqual(result["killmail_id"], 12345)
            self.assertEqual(result["zkb"]["hash"], "abc123")

    def test_raises_value_error_when_no_killmail_found(self):
        """
        Test that get_zkillboard_data raises ValueError when no killmail is found.

        :return:
        :rtype:
        """

        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            with self.assertRaises(ValueError) as cm:
                SrpRequestManager.get_zkillboard_data("12345")

            self.assertIn("Invalid Kill ID or Hash.", str(cm.exception))

    def test_raises_value_error_when_no_hash_found(self):
        """
        Test that get_zkillboard_data raises ValueError when no hash is found.

        :return:
        :rtype:
        """

        mock_response = MagicMock()
        mock_response.json.return_value = [{"killmail_id": 12345, "zkb": {}}]
        mock_response.raise_for_status.return_value = None

        with patch("requests.get", return_value=mock_response):
            with self.assertRaises(ValueError) as cm:
                SrpRequestManager.get_zkillboard_data("12345")

            self.assertIn("Invalid Kill ID or Hash.", str(cm.exception))
