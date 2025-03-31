"""
Test cases for the helper functions in the aasrp.helper.srp_data module.
"""

# Django
from django.test import TestCase, override_settings

# AA SRP
from aasrp.helper.icons import copy_to_clipboard_icon
from aasrp.helper.srp_data import (
    payout_amount_html,
    request_code_html,
    zkillboard_loss_amount_html,
)


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


class TestZkillboardLossAmountHtml(TestCase):
    """
    Test cases for the zkillboard_loss_amount_html function.
    """

    @override_settings(LANGUAGE_CODE="en")
    def test_zkillboard_loss_amount_html_returns_correct_html_locale_en(self):
        """
        Test localization of zkillboard loss amount HTML in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(zkillboard_loss_amount_html(1000), "1,000 ISK")

    @override_settings(LANGUAGE_CODE="de")
    def test_zkillboard_loss_amount_html_returns_correct_html_locale_de(self):
        """
        Test localization of zkillboard loss amount HTML in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(zkillboard_loss_amount_html(1000), "1.000 ISK")

    @override_settings(LANGUAGE_CODE="en")
    def test_zkillboard_loss_amount_html_handles_zero_locale_en(self):
        """
        Test localization of zkillboard loss amount HTML with zero in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(zkillboard_loss_amount_html(0), "0 ISK")

    @override_settings(LANGUAGE_CODE="de")
    def test_zkillboard_loss_amount_html_handles_zero_locale_de(self):
        """
        Test localization of zkillboard loss amount HTML with zero in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(zkillboard_loss_amount_html(0), "0 ISK")

    @override_settings(LANGUAGE_CODE="en")
    def test_zkillboard_loss_amount_html_handles_negative_amount_locale_en(self):
        """
        Test localization of zkillboard loss amount HTML with negative amount in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(zkillboard_loss_amount_html(-1000), "-1,000 ISK")

    @override_settings(LANGUAGE_CODE="de")
    def test_zkillboard_loss_amount_html_handles_negative_amount_locale_de(self):
        """
        Test localization of zkillboard loss amount HTML with negative amount in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(zkillboard_loss_amount_html(-1000), "-1.000 ISK")

    @override_settings(LANGUAGE_CODE="en")
    def test_zkillboard_loss_amount_html_handles_large_amount_locale_en(self):
        """
        Test localization of zkillboard loss amount HTML with a large amount in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(zkillboard_loss_amount_html(1000000000), "1,000,000,000 ISK")

    @override_settings(LANGUAGE_CODE="de")
    def test_zkillboard_loss_amount_html_handles_large_amount_locale_de(self):
        """
        Test localization of zkillboard loss amount HTML with a large amount in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(zkillboard_loss_amount_html(1000000000), "1.000.000.000 ISK")
