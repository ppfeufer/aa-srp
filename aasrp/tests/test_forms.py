"""
Tests for the forms in the aasrp app.
"""

# Standard Library
from unittest.mock import patch

# Django
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.safestring import SafeString

# AA SRP
from aasrp.constants import KILLBOARD_DATA
from aasrp.form import (
    SrpLinkForm,
    SrpLinkUpdateForm,
    SrpRequestAcceptForm,
    SrpRequestAcceptRejectedForm,
    SrpRequestForm,
    SrpRequestPayoutForm,
    SrpRequestRejectForm,
    UserSettingsForm,
    get_mandatory_form_label_text,
    sanitize_cleaned_data,
)
from aasrp.models import FleetType, SrpLink
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_fake_user


class BaseFormTestCase(BaseTestCase):
    """
    Base test case for forms
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up a SrpLink instance for testing.

        :return:
        :rtype:
        """

        super().setUpClass()

        FleetType.objects.create(name="Fleet A", is_enabled=True)
        cls.srp_link = SrpLink.objects.create(
            srp_name="Test Fleet",
            fleet_time=timezone.now(),
            fleet_type=FleetType.objects.first(),
            fleet_doctrine="Test Doctrine",
            aar_link="http://example.com/aar",
        )

        cls.user_jean_luc_picard = create_fake_user(
            character_id=1000,
            character_name="Jean Luc Picard",
        )


class TestGetMandatoryFormLabelText(BaseTestCase):
    """
    Test get_mandatory_form_label_text function
    """

    def test_returns_safe_string_with_asterisk_for_plain_text(self):
        """
        Test that the function returns a SafeString with the correct asterisk for plain text.

        :return:
        :rtype:
        """

        label = "Field Label"
        result = get_mandatory_form_label_text(label)

        self.assertIsInstance(result, SafeString)
        self.assertIn(label, result)
        self.assertIn(
            '<span aria-label="This field is mandatory" class="form-required-marker">*</span>',
            result,
        )


class TestSanitizeCleanedData(BaseTestCase):
    """
    Test sanitize_cleaned_data function
    """

    def test_return_none_when_input_is_none(self):
        """
        Test return none when input is None.

        :return:
        :rtype:
        """

        self.assertIsNone(sanitize_cleaned_data(None))

    def test_return_empty_dict_when_input_is_empty(self):
        """
        Test return empty dict when input is empty.

        :return:
        :rtype:
        """

        inp = {}

        self.assertEqual(sanitize_cleaned_data(inp), {})

    def test_non_string_values_are_untouched(self):
        """
        Test non string values are untouched.

        :return:
        :rtype:
        """

        original = {"num": 1, "lst": [1, 2], "map": {"a": "b"}, "none": None}

        self.assertEqual(sanitize_cleaned_data(original.copy()), original)

    def test_strips_simple_html_tags_from_strings(self):
        """
        Test strips simple HTML tags from strings.

        :return:
        :rtype:
        """

        inp = {"field": "<div>Hello <span>World</span></div>"}
        out = sanitize_cleaned_data(inp)

        self.assertEqual(out["field"], "Hello World")

    def test_removes_control_characters_but_keeps_linefeeds(self):
        """
        Test removes control characters and keeps linefeeds.

        :return:
        :rtype:
        """

        inp = {"text": "A\x00B\x07C\x0bD\tE\nF\x0cG\x7fH"}
        out = sanitize_cleaned_data(inp)

        self.assertNotIn("\x00", out["text"])
        self.assertNotIn("\x07", out["text"])
        self.assertNotIn("\x0b", out["text"])
        self.assertNotIn("\x0c", out["text"])
        self.assertNotIn("\x7f", out["text"])
        self.assertNotIn("\t", out["text"])
        self.assertIn("\n", out["text"])

    def test_normalizes_crlf_and_cr_to_lf_and_preserves_line_structure(self):
        """
        Test normalizes CRLF and CR to LF and preserves line structure.

        :return:
        :rtype:
        """

        inp = {"lines": "one\r\ntwo\rthree\nfour"}
        out = sanitize_cleaned_data(inp)

        self.assertNotIn("\r", out["lines"])
        self.assertEqual(out["lines"].split("\n"), ["one", "two", "three", "four"])

    def test_collapses_spaces_and_tabs_within_each_line_and_trims(self):
        """
        Test collapses spaces and tabs within each line and trims.

        :return:
        :rtype:
        """

        inp = {"p": "  lead  spaces\tand   multiple\t\tspaces  \n  second   line "}
        out = sanitize_cleaned_data(inp)

        self.assertEqual(out["p"], "lead spaces and multiple spaces\nsecond line")

    def test_mixed_fields_only_string_fields_are_sanitized(self):
        """
        Test mixed fields only string fields are sanitized.

        :return:
        :rtype:
        """

        inp = {"a": "<b>hi</b>", "b": 0, "c": "  spaced \n <i>tag</i>two  "}
        out = sanitize_cleaned_data(inp.copy())

        self.assertEqual(out["a"], "hi")
        self.assertEqual(out["b"], 0)
        self.assertEqual(out["c"], "spaced\ntagtwo")

    def test_preserves_unicode_and_emojis(self):
        """
        Test preserve unicode and emojis in sanitize_cleaned_data.

        :return:
        :rtype:
        """

        raw = "<span>Emoji 👍\n\tand    multiple   spaces</span>"
        cleaned_data = {"val": raw}

        result = sanitize_cleaned_data(cleaned_data)

        self.assertEqual(result["val"], "Emoji 👍\nand multiple spaces")


class TestSrpLinkForm(BaseTestCase):
    """
    Test SrpLinkForm
    """

    def test_saves_valid_data_correctly(self):
        """
        Test that the form saves valid data correctly.

        :return:
        :rtype:
        """

        FleetType.objects.create(name="Fleet A", is_enabled=True)
        form_data = {
            "srp_name": "Test Fleet",
            "fleet_time": "2023-10-01 12:00:00",
            "fleet_type": FleetType.objects.first().id,
            "fleet_doctrine": "Test Doctrine",
            "aar_link": "http://example.com/aar",
        }
        form = SrpLinkForm(data=form_data)

        self.assertTrue(form.is_valid())

        instance = form.save()

        self.assertEqual(instance.srp_name, "Test Fleet")
        self.assertEqual(instance.fleet_doctrine, "Test Doctrine")

    def test_fails_with_missing_required_fields(self):
        """
        Test that the form fails validation when required fields are missing.

        :return:
        :rtype:
        """

        form_data = {
            "srp_name": "",
            "fleet_time": "",
            "fleet_doctrine": "",
            "aar_link": "",
        }
        form = SrpLinkForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("srp_name", form.errors)
        self.assertIn("fleet_time", form.errors)
        self.assertIn("fleet_doctrine", form.errors)

    def test_accepts_optional_fleet_type(self):
        """
        Test that the form accepts an optional fleet_type field.

        :return:
        :rtype:
        """

        form_data = {
            "srp_name": "Test Fleet",
            "fleet_time": "2023-10-01 12:00:00",
            "fleet_type": None,
            "fleet_doctrine": "Test Doctrine",
            "aar_link": "http://example.com/aar",
        }
        form = SrpLinkForm(data=form_data)

        self.assertTrue(form.is_valid())


class TestSrpLinkUpdateForm(BaseFormTestCase):
    """
    Test SrpLinkUpdateForm
    """

    def test_saves_valid_aar_link(self):
        """
        Test that the form saves a valid aar_link correctly.

        :return:
        :rtype:
        """

        form_data = {"aar_link": "http://updated-example.com/aar"}
        form = SrpLinkUpdateForm(instance=self.srp_link, data=form_data)

        self.assertTrue(form.is_valid())

        updated_instance = form.save()

        self.assertEqual(updated_instance.aar_link, "http://updated-example.com/aar")


class TestSrpRequestForm(BaseFormTestCase):
    """
    Test SrpRequestForm
    """

    def test_accepts_valid_killboard_link(self):
        """
        Test that the form accepts a valid killboard link.

        :return:
        :rtype:
        """

        form = SrpRequestForm(
            data={
                "killboard_link": "https://zkillboard.com/kill/123456/",
                "additional_info": "Details",
            }
        )
        form.cleaned_data = {"killboard_link": "https://zkillboard.com/kill/123456/"}

        with patch(
            "aasrp.form.KILLBOARD_DATA",
            {"zKillboard": KILLBOARD_DATA.get("zKillboard")},
        ):
            self.assertEqual(
                form.clean_killboard_link(), "https://zkillboard.com/kill/123456/"
            )

    def test_validates_killboard_link_without_trailing_slash(self):
        """
        Test validates killboard link without trailing slash and adds it if required

        :return:
        :rtype:
        """

        form = SrpRequestForm(
            data={
                "killboard_link": "https://zkillboard.com/kill/123456",
                "additional_info": "Details",
            }
        )
        form.cleaned_data = {"killboard_link": "https://zkillboard.com/kill/123456"}

        with patch(
            "aasrp.form.KILLBOARD_DATA",
            {"zKillboard": KILLBOARD_DATA.get("zKillboard")},
        ):
            self.assertEqual(
                form.clean_killboard_link(), "https://zkillboard.com/kill/123456/"
            )

    def test_rejects_invalid_killboard_link(self):
        """
        Test that the form rejects an invalid killboard link.

        :return:
        :rtype:
        """

        form = SrpRequestForm(
            data={
                "killboard_link": "https://invalid.com/kill/123456/",
                "additional_info": "Details",
            }
        )
        form.cleaned_data = {"killboard_link": "https://invalid.com/kill/123456/"}

        with patch(
            "aasrp.form.KILLBOARD_DATA",
            {"zKillboard": KILLBOARD_DATA.get("zKillboard")},
        ):
            with self.assertRaises(ValidationError) as cm:
                form.clean_killboard_link()

            self.assertIn("Invalid link", str(cm.exception))

    def test_rejects_non_killmail_link(self):
        """
        Test that the form rejects a non-killmail link.

        :return:
        :rtype:
        """

        form = SrpRequestForm(
            data={
                "killboard_link": "https://zkillboard.com/ship/123456/",
                "additional_info": "Details",
            }
        )
        form.cleaned_data = {"killboard_link": "https://zkillboard.com/ship/123456/"}

        with patch(
            "aasrp.form.KILLBOARD_DATA",
            {"zKillboard": KILLBOARD_DATA.get("zKillboard")},
        ):
            with self.assertRaises(ValidationError) as cm:
                form.clean_killboard_link()

            self.assertIn(
                "Invalid link. Please post a link to a kill mail.", str(cm.exception)
            )

    def test_rejects_duplicate_killmail_link(self):
        """
        Test that the form rejects a duplicate killmail link.

        :return:
        :rtype:
        """

        form = SrpRequestForm(
            data={
                "killboard_link": "https://zkillboard.com/kill/123456/",
                "additional_info": "Details",
            }
        )
        form.cleaned_data = {"killboard_link": "https://zkillboard.com/kill/123456/"}

        with patch("aasrp.form.SrpRequest.objects.filter") as mock_filter:
            mock_filter.return_value.exists.return_value = True

            with self.assertRaises(ValidationError) as cm:
                form.clean_killboard_link()

            self.assertIn(
                "There is already an SRP request for this kill mail.", str(cm.exception)
            )


class TestSrpRequestPayoutForm(BaseTestCase):
    """
    Test SrpRequestPayoutForm
    """

    def test_accepts_valid_payout_value(self):
        """
        Test that the form accepts a valid payout value.

        :return:
        :rtype:
        """

        form_data = {"value": "100000000"}
        form = SrpRequestPayoutForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_rejects_empty_payout_value(self):
        """
        Test that the form rejects an empty payout value.

        :return:
        :rtype:
        """

        form_data = {"value": ""}
        form = SrpRequestPayoutForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("value", form.errors)

    def test_rejects_exceeding_max_length(self):
        """
        Test that the form rejects a payout value exceeding max length.

        :return:
        :rtype:
        """

        form_data = {"value": "1" * 255}
        form = SrpRequestPayoutForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("value", form.errors)


class TestSrpRequestRejectForm(BaseTestCase):
    """
    Test SrpRequestRejectForm
    """

    def test_accepts_valid_reject_reason(self):
        """
        Test that the form accepts a valid reject reason.

        :return:
        :rtype:
        """

        form_data = {"comment": "This SRP request is rejected due to invalid details."}
        form = SrpRequestRejectForm(data=form_data)

        self.assertTrue(form.is_valid())


class TestSrpRequestAcceptForm(BaseTestCase):
    """
    Test SrpRequestAcceptForm
    """

    def test_accepts_valid_comment(self):
        """
        Test that the form accepts a valid comment.

        :return:
        :rtype:
        """

        form_data = {"comment": "This SRP request is accepted."}
        form = SrpRequestAcceptForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_accepts_empty_comment(self):
        """
        Test that the form accepts an empty comment.

        :return:
        :rtype:
        """

        form_data = {"comment": ""}
        form = SrpRequestAcceptForm(data=form_data)

        self.assertTrue(form.is_valid())


class TestSrpRequestAcceptRejectedForm(BaseTestCase):
    """
    Test SrpRequestAcceptRejectedForm
    """

    def test_accepts_valid_comment(self):
        """
        Test that the form accepts a valid comment.

        :return:
        :rtype:
        """

        form_data = {"comment": "This SRP request is now accepted after review."}
        form = SrpRequestAcceptRejectedForm(data=form_data)

        self.assertTrue(form.is_valid())


class TestUserSettingsForm(BaseTestCase):
    """
    Test UserSettingsForm
    """

    def test_accepts_valid_disable_notifications_value(self):
        """
        Test that the form accepts a valid disable_notifications value.

        :return:
        :rtype:
        """

        form_data = {"disable_notifications": True}
        form = UserSettingsForm(data=form_data)

        self.assertTrue(form.is_valid())
