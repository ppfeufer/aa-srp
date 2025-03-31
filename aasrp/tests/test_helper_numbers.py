"""
Test cases for the helper.numbers module in the aasrp package.
"""

# Django
from django.test import TestCase, override_settings

# AA SRP
from aasrp.helper.numbers import l10n_number_format


class TestL10nNumberFormat(TestCase):
    """
    Test cases for the l10n_number_format function.
    """

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_integer_with_default_decimals_locale_en(self):
        """
        Test localization of an integer with default decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234), "1,234")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_integer_with_default_decimals_locale_de(self):
        """
        Test localization of an integer with default decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234), "1.234")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_float_with_default_decimals_locale_en(self):
        """
        Test localization of a float with default decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234.5678), "1,235")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_float_with_default_decimals_locale_de(self):
        """
        Test localization of a float with default decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234.5678), "1.235")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_negative_number_with_default_decimals_locale_en(self):
        """
        Test localization of a negative number with default decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(-1234.5678), "-1,235")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_negative_number_with_default_decimals_locale_de(self):
        """
        Test localization of a negative number with default decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(-1234.5678), "-1.235")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_zero_with_default_decimals_locale_en(self):
        """
        Test localization of zero with default decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(0), "0")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_zero_with_default_decimals_locale_de(self):
        """
        Test localization of zero with default decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(0), "0")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_large_number_with_default_decimals_locale_en(self):
        """
        Test localization of a large number with default decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234567890.123456), "1,234,567,890")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_large_number_with_default_decimals_locale_de(self):
        """
        Test localization of a large number with default decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234567890.123456), "1.234.567.890")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_small_number_with_default_decimals_locale_en(self):
        """
        Test localization of a small number with default decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(0.0001234), "0")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_small_number_with_default_decimals_locale_de(self):
        """
        Test localization of a small number with default decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(0.0001234), "0")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_none_value_with_default_decimals_locale_en(self):
        """
        Test localization of a None value with default decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(None), "")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_none_value_with_default_decimals_locale_de(self):
        """
        Test localization of a None value with default decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(None), "")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_integer_with_specified_decimals_locale_en(self):
        """
        Test localization of an integer with specified decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234, 2), "1,234.00")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_integer_with_specified_decimals_locale_de(self):
        """
        Test localization of an integer with specified decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234, 2), "1.234,00")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_float_with_specified_decimals_locale_en(self):
        """
        Test localization of a float with specified decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234.5678, 2), "1,234.57")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_float_with_specified_decimals_locale_de(self):
        """
        Test localization of a float with specified decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234.5678, 2), "1.234,57")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_negative_number_with_specified_decimals_locale_en(self):
        """
        Test localization of a negative number with specified decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(-1234.5678, 2), "-1,234.57")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_negative_number_with_specified_decimals_locale_de(self):
        """
        Test localization of a negative number with specified decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(-1234.5678, 2), "-1.234,57")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_zero_with_specified_decimals_locale_en(self):
        """
        Test localization of zero with specified decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(0, 2), "0.00")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_zero_with_specified_decimals_locale_de(self):
        """
        Test localization of zero with specified decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(0, 2), "0,00")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_large_number_with_specified_decimals_locale_en(self):
        """
        Test localization of a large number with specified decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234567890.123456, 2), "1,234,567,890.12")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_large_number_with_specified_decimals_locale_de(self):
        """
        Test localization of a large number with specified decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(1234567890.123456, 2), "1.234.567.890,12")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_small_number_with_specified_decimals_locale_en(self):
        """
        Test localization of a small number with specified decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(0.0001234, 6), "0.000123")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_small_number_with_specified_decimals_locale_de(self):
        """
        Test localization of a small number with specified decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(0.0001234, 6), "0,000123")

    @override_settings(LANGUAGE_CODE="en")
    def test_localizes_none_value_with_specified_decimals_locale_en(self):
        """
        Test localization of a None value with specified decimals in English locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(None, 2), "")

    @override_settings(LANGUAGE_CODE="de")
    def test_localizes_none_value_with_specified_decimals_locale_de(self):
        """
        Test localization of a None value with specified decimals in German locale.

        :return:
        :rtype:
        """

        self.assertEqual(l10n_number_format(None, 2), "")
