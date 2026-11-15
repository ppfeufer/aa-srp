"""
Unit tests for the SrpRequestManager class.
"""

# Standard Library
import json
from unittest.mock import MagicMock, patch

# Third Party
import requests

# AA SRP
from aasrp.managers import SettingManager, SettingQuerySet, SrpRequestManager
from aasrp.tests import BaseTestCase


class TestSrpRequestManagerGetKillId(BaseTestCase):
    """
    Test cases for SrpRequestManager.get_killmail_id method.
    """

    def test_extracts_killmail_id_from_supported_links(self):
        """
        Test that get_killmail_id correctly extracts the killmail ID from various supported killboard links.

        :return:
        """

        examples = (
            (
                "https://esi.evetech.net/killmails/139797181/acc89db938397301b3bf1205bcfaeee9548971da",
                "139797181",
            ),
            ("https://zkillboard.com/kill/139917484/", "139917484"),
            ("https://kb.evetools.org/kill/139934120", "139934120"),
            ("https://eve-kill.com/kill/139934120", "139934120"),
            ("https://example2.com:8080/kill/12345/?page=99#123", "12345"),
            ("https://esi.evetech.net/killmails/12345/1234567890", "12345"),
        )

        for link, expected in examples:
            with self.subTest(link=link):
                self.assertEqual(SrpRequestManager.get_killmail_id(link), expected)

    def test_rejects_links_without_numeric_killmail_id(self):
        """
        Test that get_killmail_id raises ValueError for links that do not contain a numeric killmail ID.

        :return:
        """

        for link in (
            "https://zkillboard.com/kill/",
            "https://zkillboard.com/kill/123abc/",
            "https://zkillboard.com/ship/12345/",
            "https://zkillboard.com/kill/?id=12345",
        ):
            with self.subTest(link=link), self.assertRaises(ValueError):
                SrpRequestManager.get_killmail_id(link)


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

            self.assertIn(
                "No kill mail information found in zKillboard's API response.",
                str(cm.exception),
            )

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

            self.assertIn(
                "No kill mail hash found in zKillboard's API response.",
                str(cm.exception),
            )

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

        self.assertIn("Please try again in an hour", str(context.exception))
        self.assertNotIn("HTTP error occurred", str(context.exception))
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

        self.assertIn("Please try again in an hour", str(context.exception))
        self.assertNotIn("Request timed out", str(context.exception))
        mock_logger_warning.assert_called_once_with(
            "Error fetching kill mail details: Request timed out", exc_info=True
        )

    @patch("aasrp.managers.requests.get")
    def test_raises_value_error_for_connection_error(self, mock_requests_get):
        """
        Test that get_zkillboard_data raises ValueError for connection errors.

        :param mock_requests_get:
        :type mock_requests_get:
        :return:
        :rtype:
        """

        mock_requests_get.side_effect = requests.ConnectionError("Connection reset")

        with self.assertRaises(ValueError) as context:
            SrpRequestManager.get_zkillboard_data("12345")

        self.assertIn("Please try again in an hour", str(context.exception))
        self.assertNotIn("Connection reset", str(context.exception))

    @patch("aasrp.managers.requests.get")
    def test_get_zkillboard_data_raises_valueerror_on_non_json_response(self, mock_get):
        """
        Test that get_zkillboard_data raises ValueError when the response is not valid JSON.

        :param mock_get:
        :return:
        """

        # Simulate response.json() raising JSONDecodeError
        response_mock = MagicMock()
        response_mock.raise_for_status.return_value = None
        response_mock.text = "not-json"
        response_mock.json.side_effect = json.JSONDecodeError(
            "Expecting value", "doc", 0
        )
        mock_get.return_value = response_mock

        with self.assertRaises(ValueError):
            SrpRequestManager.get_zkillboard_data(kill_id="99999")

    @patch("aasrp.managers.requests.get")
    def test_raises_valueerror_for_unexpected_inner_exception(self, mock_get):
        """
        Test that get_zkillboard_data raises ValueError for unexpected inner exceptions.

        :param mock_get:
        :return:
        """

        response_mock = MagicMock()
        response_mock.raise_for_status.return_value = None
        # Return a list of non-dict items so the generator expression raises
        # an unexpected exception when trying to access .get on an int.
        response_mock.json.return_value = [12345]
        mock_get.return_value = response_mock

        with self.assertRaises(ValueError) as cm:
            SrpRequestManager.get_zkillboard_data(kill_id="12345")

        self.assertEqual(str(cm.exception), "Invalid Kill ID or Hash.")
        self.assertIsInstance(cm.exception.__cause__, Exception)


class TestSrpRequestManagerGetInsuranceForShipType(BaseTestCase):
    """
    Test cases for SrpRequestManager.get_insurance_for_ship_type method.
    """

    @patch("aasrp.managers.ESIHandler.result")
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

    @patch("aasrp.managers.ESIHandler.result")
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

    @patch("aasrp.managers.ESIHandler.result")
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

    @patch("aasrp.managers.ESIHandler.result")
    @patch("aasrp.managers.esi")
    def test_returns_none_when_esi_fails(self, mock_esi, mock_esi_result):
        """
        Test that get_insurance_for_ship_type returns None when the ESI call fails.

        :param mock_esi:
        :type mock_esi:
        :param mock_esi_result:
        :type mock_esi_result:
        :return:
        :rtype:
        """

        mock_esi_result.return_value = None

        result = SrpRequestManager.get_insurance_for_ship_type(123)

        self.assertIsNone(result)


class TestSrpRequestManagerGetKillmailData(BaseTestCase):
    """
    Test cases for SrpRequestManager.get_killmail_data method.
    """

    @patch("aasrp.managers.killboard_settings")
    @patch("aasrp.managers.SrpRequestManager.get_zkillboard_data")
    def test_returns_expected_data_for_non_esi_killmail_link(
        self, mock_get_zkillboard_data, mock_killboard_settings
    ):
        """
        Test that get_killmail_data returns the expected data for a non-ESI killmail link.

        :param mock_get_zkillboard_data:
        :param mock_killboard_settings:
        :return:
        """

        mock_killboard_settings.return_value = {
            "base_url_regex": r"^https://esi\.evetech\.net/killmails/",
            "api_url": "https://zkillboard.com/post/",
        }
        mock_get_zkillboard_data.return_value = {
            "victim": {"character_id": 456, "ship_type_id": 123},
            "zkb": {"totalValue": 5000000, "hash": "hash123"},
        }

        result = SrpRequestManager.get_killmail_data(
            "https://zkillboard.com/kill/12345/", "totalValue"
        )

        self.assertEqual(
            result,
            {
                "killmail_id": "12345",
                "ship_type_id": 123,
                "ship_value": 5000000,
                "victim_id": 456,
            },
        )

    @patch("aasrp.managers.killboard_settings")
    @patch("aasrp.managers.requests.post")
    def test_returns_expected_data_for_esi_killmail_link(
        self, mock_post, mock_killboard_settings
    ):
        """
        Test that get_killmail_data returns the expected data for an ESI killmail link.

        :param mock_post:
        :param mock_killboard_settings:
        :return:
        """

        mock_killboard_settings.return_value = {
            "base_url_regex": r"^https://esi\.evetech\.net/killmails/",
            "api_url": "https://zkillboard.com/post/",
        }

        response_mock = MagicMock()
        response_mock.raise_for_status.return_value = None
        response_mock.json.return_value = {
            "package": [
                {
                    "killmail_id": 12345,
                    "victim": {"character_id": 456, "ship_type_id": 123},
                    "zkb": {"totalValue": 5000000, "hash": "hash123"},
                }
            ]
        }
        mock_post.return_value = response_mock

        result = SrpRequestManager.get_killmail_data(
            "https://esi.evetech.net/killmails/12345/hash123", "totalValue"
        )

        self.assertEqual(
            result,
            {
                "killmail_id": "12345",
                "ship_type_id": 123,
                "ship_value": 5000000,
                "victim_id": 456,
            },
        )

    @patch("aasrp.managers.killboard_settings")
    @patch("aasrp.managers.SrpRequestManager.get_zkillboard_data")
    def test_defaults_ship_value_to_zero_when_requested_field_is_missing(
        self, mock_get_zkillboard_data, mock_killboard_settings
    ):
        """
        Test that get_killmail_data defaults ship_value to zero when the requested field is missing.

        :param mock_get_zkillboard_data:
        :param mock_killboard_settings:
        :return:
        """

        mock_killboard_settings.return_value = {
            "base_url_regex": r"^https://esi\.evetech\.net/killmails/",
            "api_url": "https://zkillboard.com/post/",
        }
        mock_get_zkillboard_data.return_value = {
            "victim": {"character_id": 456, "ship_type_id": 123},
            "zkb": {"hash": "hash123"},
        }

        result = SrpRequestManager.get_killmail_data(
            "https://zkillboard.com/kill/12345/", "nonexistent_field"
        )

        self.assertEqual(result["ship_value"], 0)
        self.assertEqual(result["killmail_id"], "12345")

    @patch("aasrp.managers.killboard_settings")
    @patch("aasrp.managers.requests.post")
    def test_raises_value_error_when_post_to_zkillboard_fails(
        self, mock_post, mock_killboard_settings
    ):
        """
        Test that get_killmail_data raises ValueError when the POST request to zKillboard fails.

        :param mock_post:
        :param mock_killboard_settings:
        :return:
        """

        mock_killboard_settings.return_value = {
            "base_url_regex": r"^https://esi\.evetech\.net/killmails/",
            "api_url": "https://zkillboard.com/post/",
        }
        mock_post.side_effect = requests.Timeout("Request timed out")

        with self.assertRaises(ValueError) as context:
            SrpRequestManager.get_killmail_data(
                "https://esi.evetech.net/killmails/12345/hash123", "totalValue"
            )

        self.assertIn("Please try again in an hour", str(context.exception))

    @patch("aasrp.managers.killboard_settings")
    @patch("aasrp.managers.requests.post")
    def test_raises_value_error_when_esi_post_response_is_not_json(
        self, mock_post, mock_killboard_settings
    ):
        """
        Test that get_killmail_data raises ValueError when the ESI POST response is not valid JSON.

        :param mock_post:
        :param mock_killboard_settings:
        :return:
        """

        mock_killboard_settings.return_value = {
            "base_url_regex": r"^https://esi\.evetech\.net/killmails/",
            "api_url": "https://zkillboard.com/post/",
        }

        response_mock = MagicMock()
        response_mock.raise_for_status.return_value = None
        response_mock.text = "not-json"
        response_mock.json.side_effect = json.JSONDecodeError(
            "Expecting value", "doc", 0
        )
        mock_post.return_value = response_mock

        with self.assertRaises(ValueError) as context:
            SrpRequestManager.get_killmail_data(
                "https://esi.evetech.net/killmails/12345/hash123", "totalValue"
            )

        self.assertIn("unparseable response", str(context.exception).lower())


class TestSettingQuerySet(BaseTestCase):
    """
    Test cases for the SettingQuerySet class.
    """

    def test_prevents_deletion_of_settings(self):
        """
        Test that delete method prevents deletion of settings and instead updates them.

        :return:
        :rtype:
        """

        queryset = SettingQuerySet(model=MagicMock())

        with patch("django.db.models.QuerySet.update", return_value=1) as mock_update:
            result = queryset.delete()

            self.assertEqual(result, 1)
            mock_update.assert_called_once()

    def test_handles_no_settings_to_update(self):
        """
        Test that delete method handles the case where there are no settings to update.

        :return:
        :rtype:
        """

        queryset = SettingQuerySet(model=MagicMock())

        with patch("django.db.models.QuerySet.update", return_value=0) as mock_update:
            result = queryset.delete()

            self.assertEqual(result, 0)
            mock_update.assert_called_once()


class TestSettingManager(BaseTestCase):
    """
    Test cases for the SettingManager class.
    """

    def test_retrieves_setting_value_by_key(self):
        manager = SettingManager()
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = MagicMock(my_setting="value")
        with patch.object(manager, "get_queryset", return_value=mock_queryset):
            result = manager.get_setting("my_setting")
            self.assertEqual(result, "value")

    def test_returns_none_if_setting_key_does_not_exist(self):
        manager = SettingManager()
        mock_queryset = MagicMock()
        mock_queryset.first.return_value = None
        with patch.object(manager, "get_queryset", return_value=mock_queryset):
            result = manager.get_setting("non_existent_key")
            self.assertIsNone(result)

    def test_returns_custom_queryset_instance(self):
        manager = SettingManager()
        queryset = manager.get_queryset()
        self.assertIsInstance(queryset, SettingQuerySet)
