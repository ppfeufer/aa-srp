"""
Tests for form.py
"""

# Standard Library
from unittest.mock import patch

# Django
from django.core.exceptions import ValidationError
from django.test import TestCase

# AA SRP
from aasrp.constants import KILLBOARD_DATA
from aasrp.form import SrpRequestForm


class TestSrpRequestForm(TestCase):
    """
    Test SrpRequestForm
    """

    def test_validates_killboard_link_with_trailing_slash(self):
        """
        Test validates killboard link with trailing slash

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

    def test_raises_error_for_invalid_killboard_link(self):
        """
        Test raises error for invalid killboard link

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

    def test_raises_error_for_non_killmail_link(self):
        """
        Test raises error for non-killmail link

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

    def test_raises_error_if_srp_request_already_exists(self):
        """
        Test raises error if SRP request already exists for the given killmail

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
