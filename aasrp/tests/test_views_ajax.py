"""
Tests for AJAX views in the aasrp app.
"""

# Django
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.datetime_safe import datetime

# Alliance Auth (External Libs)
from app_utils.testing import create_fake_user

# AA SRP
from aasrp.models import SrpLink
from aasrp.tests import BaseTestCase


class BaseViewsTestCase(BaseTestCase):
    """
    Base test case for views tests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up the test class by creating fake users.

        :return:
        :rtype:
        """

        super().setUpClass()

        cls.user_jean_luc_picard = create_fake_user(
            character_id=1000,
            character_name="Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )
        cls.user_wesley_crusher = create_fake_user(
            character_id=1001,
            character_name="Wesley Crusher",
            permissions=["aasrp.basic_access"],
        )

        cls.srp_link_active = SrpLink(
            srp_name="Active SRP",
            srp_status=SrpLink.Status.ACTIVE,
            creator=cls.user_jean_luc_picard,
            fleet_time=datetime.now(),
            srp_code=get_random_string(length=16),
        )
        cls.srp_link_active.save()

        cls.srp_link_closed = SrpLink(
            srp_name="Closed SRP",
            srp_status=SrpLink.Status.CLOSED,
            creator=cls.user_jean_luc_picard,
            fleet_time=datetime.now(),
            srp_code=get_random_string(length=16),
        )
        cls.srp_link_closed.save()


class DashboardSrpLinksDataTests(BaseViewsTestCase):
    """
    Tests for the dashboard_srp_links_data view.
    """

    def test_returns_active_srp_links(self):
        """
        Test that the view returns only active SRP links.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_wesley_crusher)

        response = self.client.get(reverse("aasrp:ajax_dashboard_srp_links_data"))

        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["srp_name"], "Active SRP")

    def test_returns_all_srp_links_when_show_all_is_true(self):
        """
        Test that the view returns all SRP links when show_all_links is True.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_wesley_crusher)

        url = reverse("aasrp:ajax_dashboard_srp_links_all_data")
        response = self.client.get(url)

        self.assertEqual(len(response.json()), 2)

    def test_includes_copy_icon_for_active_links(self):
        """
        Test that the view includes a copy icon for active SRP links.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_wesley_crusher)
        url = reverse("aasrp:ajax_dashboard_srp_links_data")

        response = self.client.get(url)

        self.assertIn(
            '<span class="copy-to-clipboard-icon">',
            response.json()[0]["srp_code"]["display"],
        )
