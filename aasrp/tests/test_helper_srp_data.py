"""
Test cases for the helper functions in the aasrp.helper.srp_data module.
"""

# Standard Library
from unittest.mock import MagicMock, patch

# Django
from django.test import TestCase, override_settings

# AA SRP
from aasrp.helper.icons import copy_to_clipboard_icon
from aasrp.helper.srp_data import (
    attempt_to_re_add_ship_information_to_request,
    localized_isk_value,
    payout_amount_html,
    request_code_html,
    request_fleet_details_html,
)
from aasrp.models import SrpLink, SrpRequest


class TestPayoutAmountHtml(TestCase):
    """
    Test cases for the payout_amount_html function.
    """

    @override_settings(LANGUAGE_CODE="en")
    def test_payout_amount_html_returns_correct_html_locale_en(self):
        """
        Test localization of payout amount HTML in English locale.

        :return:
        :rtype:
        """

        result = payout_amount_html(1000)

        self.assertIn(
            '<span class="srp-payout-amount d-block cursor-pointer">1,000 ISK</span>',
            result,
        )
        self.assertIn('data-clipboard-text="1000"', result)

    @override_settings(LANGUAGE_CODE="de")
    def test_payout_amount_html_returns_correct_html_locale_de(self):
        """
        Test localization of payout amount HTML in German locale.

        :return:
        :rtype:
        """

        result = payout_amount_html(1000)

        self.assertIn(
            '<span class="srp-payout-amount d-block cursor-pointer">1.000 ISK</span>',
            result,
        )
        self.assertIn('data-clipboard-text="1000"', result)

    @override_settings(LANGUAGE_CODE="en")
    def test_payout_amount_html_handles_zero_locale_en(self):
        """
        Test localization of payout amount HTML with zero in English locale.

        :return:
        :rtype:
        """

        result = payout_amount_html(0)

        self.assertIn(
            '<span class="srp-payout-amount d-block cursor-pointer">0 ISK</span>',
            result,
        )
        self.assertIn('data-clipboard-text="0"', result)

    @override_settings(LANGUAGE_CODE="de")
    def test_payout_amount_html_handles_zero_locale_de(self):
        """
        Test localization of payout amount HTML with zero in German locale.

        :return:
        :rtype:
        """

        result = payout_amount_html(0)

        self.assertIn(
            '<span class="srp-payout-amount d-block cursor-pointer">0 ISK</span>',
            result,
        )
        self.assertIn('data-clipboard-text="0"', result)

    @override_settings(LANGUAGE_CODE="en")
    def test_payout_amount_html_handles_negative_amount_locale_en(self):
        """
        Test localization of payout amount HTML with negative amount in English locale.

        :return:
        :rtype:
        """

        result = payout_amount_html(-1000)

        self.assertIn(
            '<span class="srp-payout-amount d-block cursor-pointer">-1,000 ISK</span>',
            result,
        )
        self.assertIn('data-clipboard-text="-1000"', result)

    @override_settings(LANGUAGE_CODE="de")
    def test_payout_amount_html_handles_negative_amount_locale_de(self):
        """
        Test localization of payout amount HTML with negative amount in German locale.

        :return:
        :rtype:
        """

        result = payout_amount_html(-1000)

        self.assertIn(
            '<span class="srp-payout-amount d-block cursor-pointer">-1.000 ISK</span>',
            result,
        )
        self.assertIn('data-clipboard-text="-1000"', result)

    @override_settings(LANGUAGE_CODE="en")
    def test_payout_amount_html_handles_large_amount_locale_en(self):
        """
        Test localization of payout amount HTML with a large amount in English locale.

        :return:
        :rtype:
        """

        result = payout_amount_html(1000000000)

        self.assertIn(
            '<span class="srp-payout-amount d-block cursor-pointer">1,000,000,000 ISK</span>',
            result,
        )
        self.assertIn('data-clipboard-text="1000000000"', result)

    @override_settings(LANGUAGE_CODE="de")
    def test_payout_amount_html_handles_large_amount_locale_de(self):
        """
        Test localization of payout amount HTML with a large amount in German locale.

        :return:
        :rtype:
        """

        result = payout_amount_html(1000000000)

        self.assertIn(
            '<span class="srp-payout-amount d-block cursor-pointer">1.000.000.000 ISK</span>',
            result,
        )
        self.assertIn('data-clipboard-text="1000000000"', result)


class TestRequestCodeHtml(TestCase):
    """
    Test cases for the request_code_html function.
    """

    def test_request_code_html_returns_correct_html(self):
        """
        Test returning correct HTML for request code.

        :return:
        :rtype:
        """

        result = request_code_html("ABC123")

        icon = copy_to_clipboard_icon(
            data="ABC123", title="Copy request code to clipboard"
        )

        self.assertEqual(result, f"ABC123<sup>{icon}</sup>")


class TestLocalizedIskValue(TestCase):
    """
    Test cases for the localized_isk_value function.
    """

    @override_settings(LANGUAGE_CODE="en")
    def test_localized_isk_value_returns_correct_html_locale_en(self):
        """
        Test localization of ISK value in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(localized_isk_value(1000), "1,000 ISK")

    @override_settings(LANGUAGE_CODE="de")
    def test_localized_isk_value_returns_correct_html_locale_de(self):
        """
        Test localization of ISK value in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(localized_isk_value(1000), "1.000 ISK")

    @override_settings(LANGUAGE_CODE="en")
    def test_localized_isk_value_handles_zero_locale_en(self):
        """
        Test localization of ISK value with zero in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(localized_isk_value(0), "0 ISK")

    @override_settings(LANGUAGE_CODE="de")
    def test_localized_isk_value_handles_zero_locale_de(self):
        """
        Test localization of ISK value with zero in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(localized_isk_value(0), "0 ISK")

    @override_settings(LANGUAGE_CODE="en")
    def test_localized_isk_value_handles_negative_amount_locale_en(self):
        """
        Test localization of ISK value with negative amount in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(localized_isk_value(-1000), "-1,000 ISK")

    @override_settings(LANGUAGE_CODE="de")
    def test_localized_isk_value_handles_negative_amount_locale_de(self):
        """
        Test localization of ISK value with negative amount in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(localized_isk_value(-1000), "-1.000 ISK")

    @override_settings(LANGUAGE_CODE="en")
    def test_localized_isk_value_handles_large_amount_locale_en(self):
        """
        Test localization of ISK value with a large amount in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(localized_isk_value(1000000000), "1,000,000,000 ISK")

    @override_settings(LANGUAGE_CODE="de")
    def test_localized_isk_value_handles_large_amount_locale_de(self):
        """
        Test localization of ISK value with a large amount in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(localized_isk_value(1000000000), "1.000.000.000 ISK")


class TestRequestFleetDetailsHtml(TestCase):
    """
    Test cases for the request_fleet_details_html function.
    """

    def test_request_fleet_details_html_returns_correct_html(self):
        """
        Test returning correct HTML for fleet details.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="Fleet Alpha", srp_code="FA123")
        srp_request = SrpRequest(srp_link=srp_link, request_code="REQ123")
        result = request_fleet_details_html(srp_request)

        self.assertIn("<p>Fleet Alpha</p>", result)
        self.assertIn("SRP code: FA123", result)
        self.assertIn("Request code: REQ123", result)

    def test_request_fleet_details_html_handles_empty_srp_name(self):
        """
        Test returning correct HTML for fleet details with empty SRP name.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="", srp_code="FA123")
        srp_request = SrpRequest(srp_link=srp_link, request_code="REQ123")
        result = request_fleet_details_html(srp_request)

        self.assertIn("<p></p>", result)
        self.assertIn("SRP code: FA123", result)
        self.assertIn("Request code: REQ123", result)

    def test_request_fleet_details_html_handles_empty_request_code(self):
        """
        Test returning correct HTML for fleet details with empty request code.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="Fleet Alpha", srp_code="FA123")
        srp_request = SrpRequest(srp_link=srp_link, request_code="")
        result = request_fleet_details_html(srp_request)

        self.assertIn("<p>Fleet Alpha</p>", result)
        self.assertIn("SRP code: FA123", result)
        self.assertIn("Request code: ", result)

    def test_request_fleet_details_html_handles_special_characters(self):
        """
        Test returning correct HTML for fleet details with special characters.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="Fleet @lpha", srp_code="FA!23")
        srp_request = SrpRequest(srp_link=srp_link, request_code="REQ!23")
        result = request_fleet_details_html(srp_request)

        self.assertIn("<p>Fleet @lpha</p>", result)
        self.assertIn("SRP code: FA!23", result)
        self.assertIn("Request code: REQ!23", result)


class TestAttemptToReAddShipInformation(TestCase):
    """
    Test cases for the attempt_to_re_add_ship_information_to_request function.
    """

    def test_re_adds_ship_information_when_missing(self):
        """
        Test re-adding ship information when missing.

        :return:
        :rtype:
        """

        srp_request = MagicMock()
        srp_request.killboard_link = "https://zkillboard.com/kill/123456/"
        srp_request.ship = None

        mock_ship = MagicMock(id=123)
        mock_ship.name = "Mock Ship"

        with (
            patch("aasrp.models.SrpRequest.objects.get_kill_id", return_value="123456"),
            patch(
                "aasrp.models.SrpRequest.objects.get_kill_data",
                return_value=(123, 1000000, 456),
            ),
            patch(
                "eveuniverse.models.EveType.objects.get_or_create_esi",
                return_value=(mock_ship, True),
            ),
        ):
            updated_request = attempt_to_re_add_ship_information_to_request(srp_request)

        self.assertEqual(updated_request.ship_name, "Mock Ship")

    def test_does_not_modify_ship_information_if_already_present(self):
        """
        Test that ship information is not modified if already present.

        :return:
        :rtype:
        """

        srp_request = MagicMock()
        srp_request.killboard_link = "https://zkillboard.com/kill/123456/"
        mock_ship = MagicMock(id=123)
        mock_ship.name = "Existing Ship"
        srp_request.ship = mock_ship
        srp_request.ship_name = "Existing Ship"  # <-- Set this explicitly

        with (
            patch("aasrp.models.SrpRequest.objects.get_kill_id") as mock_get_kill_id,
            patch(
                "aasrp.models.SrpRequest.objects.get_kill_data"
            ) as mock_get_kill_data,
            patch(
                "eveuniverse.models.EveType.objects.get_or_create_esi"
            ) as mock_get_or_create_esi,
        ):
            updated_request = attempt_to_re_add_ship_information_to_request(srp_request)

        mock_get_kill_id.assert_not_called()
        mock_get_kill_data.assert_not_called()
        mock_get_or_create_esi.assert_not_called()
        self.assertEqual(updated_request.ship_name, "Existing Ship")
        self.assertIsNotNone(updated_request.ship)
