"""
Test the admin interface.
"""

# Standard Library
from http import HTTPStatus

# Django
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

# AA SRP
from aasrp.models import FleetType


class TestFleetTypeAdmin(TestCase):
    """
    Test the FleetType admin interface.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the admin interface tests.

        :return:
        :rtype:
        """

        cls.admin_user = User.objects.create_superuser(
            "admin", "admin@example.com", "password"
        )
        cls.client = Client()
        cls.client.login(username="admin", password="password")
        cls.fleet_type = FleetType.objects.create(name="Test Fleet", is_enabled=True)

    def test_admin_page_loads(self):
        """
        Test that the admin page loads correctly.

        :return:
        :rtype:
        """

        url = reverse("admin:aasrp_fleettype_changelist")
        self.client.login(username="admin", password="password")
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_admin_form_saves_valid_data(self):
        """
        Test that the admin form saves valid data correctly.

        :return:
        :rtype:
        """

        url = reverse("admin:aasrp_fleettype_change", args=[self.fleet_type.pk])
        self.client.login(username="admin", password="password")
        data = {
            "name": "Updated Fleet",
            "is_enabled": False,
            "_save": "Save",  # Include the save button name to simulate form submission
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.fleet_type.refresh_from_db()
        self.assertEqual(self.fleet_type.name, "Updated Fleet")
        self.assertFalse(self.fleet_type.is_enabled)

    def test_activate_action_activates_selected_fleet_types(self):
        """
        Test that the activate action activates selected fleet types.

        :return:
        :rtype:
        """

        url = reverse("admin:aasrp_fleettype_changelist")
        self.client.login(username="admin", password="password")
        data = {
            "action": "activate",
            "_selected_action": [self.fleet_type.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.fleet_type.refresh_from_db()
        self.assertTrue(self.fleet_type.is_enabled)

    def test_deactivate_action_deactivates_selected_fleet_types(self):
        """
        Test that the deactivate action deactivates selected fleet types.

        :return:
        :rtype:
        """

        url = reverse("admin:aasrp_fleettype_changelist")
        self.client.login(username="admin", password="password")
        data = {
            "action": "deactivate",
            "_selected_action": [self.fleet_type.pk],
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.fleet_type.refresh_from_db()
        self.assertFalse(self.fleet_type.is_enabled)
