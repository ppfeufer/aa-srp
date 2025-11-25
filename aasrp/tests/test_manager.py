"""
Unit tests for the SrpRequestManager class.
"""

# Standard Library
from unittest.mock import MagicMock, patch

# Third Party
import requests

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

    @patch("aasrp.managers.requests.get")
    @patch("aasrp.managers.logger.warning")
    def test_raises_value_error_for_http_error(
        self, mock_logger_warning, mock_requests_get
    ):
        """
        Test that get_zkillboard_data raises ValueError for HTTP errors.

        :param mock_logger_warning:
        :type mock_logger_warning:
        :param mock_requests_get:
        :type mock_requests_get:
        :return:
        :rtype:
        """

        mock_requests_get.side_effect = requests.HTTPError("HTTP error occurred")

        with self.assertRaises(ValueError) as context:
            SrpRequestManager.get_zkillboard_data("12345")

        self.assertIn("HTTP error occurred", str(context.exception))
        mock_logger_warning.assert_called_once_with(
            "Error fetching kill mail details: HTTP error occurred", exc_info=True
        )

    @patch("aasrp.managers.requests.get")
    @patch("aasrp.managers.logger.warning")
    def test_raises_value_error_for_timeout_error(
        self, mock_logger_warning, mock_requests_get
    ):
        """
        Test that get_zkillboard_data raises ValueError for timeout errors.

        :param mock_logger_warning:
        :type mock_logger_warning:
        :param mock_requests_get:
        :type mock_requests_get:
        :return:
        :rtype:
        """

        mock_requests_get.side_effect = requests.Timeout("Request timed out")

        with self.assertRaises(ValueError) as context:
            SrpRequestManager.get_zkillboard_data("12345")

        self.assertIn("Request timed out", str(context.exception))
        mock_logger_warning.assert_called_once_with(
            "Error fetching kill mail details: Request timed out", exc_info=True
        )


class TestSrpRequestManagerGetInsuranceForShipType(BaseTestCase):
    """
    Test cases for SrpRequestManager.get_insurance_for_ship_type method.
    """

    @patch("aasrp.managers.esi_handler.result")
    @patch("aasrp.managers.esi")
    def test_returns_insurance_details_for_valid_ship_type(
        self, mock_esi, mock_esi_result
    ):
        """
        Test that get_insurance_for_ship_type returns correct insurance details for a valid ship type.

        :param mock_esi:
        :type mock_esi:
        :param mock_esi_result:
        :type mock_esi_result:
        :return:
        :rtype:
        """

        mock_insurance_data = [
            MagicMock(type_id=123, insurance="Platinum"),
            MagicMock(type_id=456, insurance="Gold"),
        ]
        mock_esi_result.return_value = mock_insurance_data
        mock_esi.client.Insurance.GetInsurancePrices.return_value = MagicMock()

        result = SrpRequestManager.get_insurance_for_ship_type(123)

        self.assertEqual(result.insurance, "Platinum")

    @patch("aasrp.managers.esi_handler.result")
    @patch("aasrp.managers.esi")
    def test_returns_none_for_invalid_ship_type(self, mock_esi, mock_esi_result):
        """
        Test that get_insurance_for_ship_type returns None for an invalid ship type.

        :param mock_esi:
        :type mock_esi:
        :param mock_esi_result:
        :type mock_esi_result:
        :return:
        :rtype:
        """

        mock_insurance_data = [
            MagicMock(type_id=123, insurance="Platinum"),
            MagicMock(type_id=456, insurance="Gold"),
        ]
        mock_esi_result.return_value = mock_insurance_data
        mock_esi.client.Insurance.GetInsurancePrices.return_value = MagicMock()

        result = SrpRequestManager.get_insurance_for_ship_type(789)

        self.assertIsNone(result)

    @patch("aasrp.managers.esi_handler.result")
    @patch("aasrp.managers.esi")
    def test_handles_empty_insurance_data(self, mock_esi, mock_esi_result):
        """
        Test that get_insurance_for_ship_type handles empty insurance data.

        :param mock_esi:
        :type mock_esi:
        :param mock_esi_result:
        :type mock_esi_result:
        :return:
        :rtype:
        """

        mock_esi_result.return_value = []
        mock_esi.client.Insurance.GetInsurancePrices.return_value = MagicMock()

        result = SrpRequestManager.get_insurance_for_ship_type(123)

        self.assertIsNone(result)


class TestSrpRequestManagerKetKillData(BaseTestCase):
    """
    Test cases for SrpRequestManager.get_kill_data method.
    """

    @patch("aasrp.managers.esi")
    @patch("aasrp.managers.SrpRequestManager.get_zkillboard_data")
    @patch("aasrp.managers.esi_handler.result")
    def test_returns_correct_kill_data(
        self, mock_esi_result, mock_get_zkillboard_data, mock_esi
    ):
        """
        Test that get_kill_data returns correct kill data.
        """
        mock_get_zkillboard_data.return_value = {
            "zkb": {"hash": "test_hash", "loss_value": 5000000}
        }
        mock_esi_result.return_value = MagicMock(
            victim=MagicMock(ship_type_id=123, character_id=456)
        )

        mock_operation = MagicMock()
        mock_esi.client.Killmails.GetKillmailsKillmailIdKillmailHash.return_value = (
            mock_operation
        )

        result = SrpRequestManager.get_kill_data("12345", "loss_value")

        self.assertEqual(result, (123, 5000000, 456))

    @patch("aasrp.managers.SrpRequestManager.get_zkillboard_data")
    @patch("aasrp.managers.esi_handler.result")
    def test_raises_value_error_for_missing_killmail_hash(
        self, mock_esi_result, mock_get_zkillboard_data
    ):
        """
        Test that get_kill_data raises ValueError when killmail hash is missing.

        :param mock_esi_result:
        :type mock_esi_result:
        :param mock_get_zkillboard_data:
        :type mock_get_zkillboard_data:
        :return:
        :rtype:
        """

        mock_get_zkillboard_data.side_effect = ValueError("No kill mail hash found")

        with self.assertRaises(ValueError) as context:
            SrpRequestManager.get_kill_data("12345", "loss_value")

        self.assertIn("No kill mail hash found", str(context.exception))

    @patch("aasrp.managers.SrpRequestManager.get_zkillboard_data")
    @patch("aasrp.managers.esi_handler.result")
    def test_raises_value_error_for_invalid_killmail_id(
        self, mock_esi_result, mock_get_zkillboard_data
    ):
        """
        Test that get_kill_data raises ValueError for an invalid killmail ID.

        :param mock_esi_result:
        :type mock_esi_result:
        :param mock_get_zkillboard_data:
        :type mock_get_zkillboard_data:
        :return:
        :rtype:
        """

        mock_get_zkillboard_data.side_effect = ValueError("Invalid Kill ID or Hash.")

        with self.assertRaises(ValueError) as context:
            SrpRequestManager.get_kill_data("invalid_id", "loss_value")

        self.assertIn("Invalid Kill ID or Hash.", str(context.exception))

    @patch("aasrp.managers.esi")
    @patch("aasrp.managers.SrpRequestManager.get_zkillboard_data")
    @patch("aasrp.managers.esi_handler.result")
    def test_handles_missing_loss_value_field(
        self, mock_esi_result, mock_get_zkillboard_data, mock_esi
    ):
        mock_get_zkillboard_data.return_value = {"zkb": {"hash": "test_hash"}}
        mock_esi_result.return_value = MagicMock(
            victim=MagicMock(ship_type_id=123, character_id=456)
        )

        mock_operation = MagicMock()
        mock_esi.client.Killmails.GetKillmailsKillmailIdKillmailHash.return_value = (
            mock_operation
        )

        result = SrpRequestManager.get_kill_data("12345", "nonexistent_field")

        self.assertEqual(result, (123, 0, 456))
