"""
Test the admin interface.
"""

# Standard Library
from http import HTTPStatus
from unittest.mock import MagicMock, patch

# Django
from django.contrib import admin
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

# AA SRP
from aasrp.admin import RequestCommentAdmin, SrpLinkAdmin, SrpRequestAdmin
from aasrp.models import FleetType, RequestComment


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
            username="admin", email="admin@example.com", password="password"
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

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)

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
        response = self.client.post(path=url, data=data)

        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
        self.fleet_type.refresh_from_db()
        self.assertEqual(first=self.fleet_type.name, second="Updated Fleet")
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
        response = self.client.post(path=url, data=data, follow=True)

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
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
        response = self.client.post(path=url, data=data, follow=True)

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.fleet_type.refresh_from_db()
        self.assertFalse(self.fleet_type.is_enabled)


class TestRequestCommentAdmin(TestCase):
    """
    Test the RequestComment admin interface.
    """

    def test_displays_correct_srp_code_in_admin(self):
        """
        Test that the SRP code is displayed correctly in the admin interface.

        :return:
        :rtype:
        """

        request_comment = MagicMock()
        request_comment.srp_request.srp_link.srp_code = "SRP123"

        admin_instance = RequestCommentAdmin(
            model=RequestComment, admin_site=admin.site
        )
        result = admin_instance._srp_code(request_comment)

        self.assertEqual(first=result, second="SRP123")

    def test_displays_correct_request_code_in_admin(self):
        """
        Test that the request code is displayed correctly in the admin interface.

        :return:
        :rtype:
        """

        request_comment = MagicMock()
        request_comment.srp_request.request_code = "REQ456"

        admin_instance = RequestCommentAdmin(
            model=RequestComment, admin_site=admin.site
        )
        result = admin_instance._request_code(request_comment)

        self.assertEqual(first=result, second="REQ456")

    def test_displays_correct_requestor_name_in_admin(self):
        """
        Test that the requestor name is displayed correctly in the admin interface.

        :return:
        :rtype:
        """

        request_comment = MagicMock()
        request_comment.srp_request.creator = MagicMock()

        with patch(
            target="aasrp.admin.get_main_character_name_from_user",
            return_value="John Doe",
        ):
            admin_instance = RequestCommentAdmin(
                model=RequestComment, admin_site=admin.site
            )
            result = admin_instance._requestor(request_comment)

        self.assertEqual(first=result, second="John Doe")

    def test_displays_correct_character_name_in_admin(self):
        request_comment = MagicMock()
        request_comment.srp_request.character.character_name = "Jane Doe"

        admin_instance = RequestCommentAdmin(
            model=RequestComment, admin_site=admin.site
        )
        result = admin_instance._character(request_comment)

        self.assertEqual(first=result, second="Jane Doe")


class TestSrpRequestAdmin(TestCase):
    """
    Test the SrpRequest admin interface.
    """

    def test_displays_correct_requestor_name_for_valid_creator(self):
        """
        Test that the requestor name is displayed correctly when the creator is valid.

        :return:
        :rtype:
        """

        srp_request = MagicMock()
        srp_request.creator = MagicMock()

        with patch(
            target="aasrp.admin.get_main_character_name_from_user",
            return_value="John Doe",
        ):
            result = SrpRequestAdmin._requestor(srp_request)

        self.assertEqual(first=result, second="John Doe")

    def test_handles_missing_creator_gracefully(self):
        """
        Test that the requestor name is None when the creator is missing.

        :return:
        :rtype:
        """

        srp_request = MagicMock()
        srp_request.creator = None

        with patch(
            target="aasrp.admin.get_main_character_name_from_user", return_value=None
        ):
            result = SrpRequestAdmin._requestor(srp_request)

        self.assertIsNone(result)

    def test_displays_correct_srp_code_for_valid_link(self):
        """
        Test that the SRP code is displayed correctly when the SRP link is valid.

        :return:
        :rtype:
        """

        srp_request = MagicMock()
        srp_request.srp_link.srp_code = "SRP123"

        admin_instance = SrpRequestAdmin(model=RequestComment, admin_site=admin.site)
        result = admin_instance._srp_code(srp_request)

        self.assertEqual(first=result, second="SRP123")


class TestSrpLinkAdmin(TestCase):
    """
    Test the SrpLink admin interface.
    """

    def test_displays_correct_creator_name_for_valid_creator(self):
        """
        Test that the creator name is displayed correctly when the creator is valid.

        :return:
        :rtype:
        """

        srp_link = MagicMock()
        srp_link.creator = MagicMock()

        with patch(
            target="aasrp.admin.get_main_character_name_from_user",
            return_value="Jane Doe",
        ):
            result = SrpLinkAdmin._creator(srp_link)

        self.assertEqual(first=result, second="Jane Doe")

    def test_handles_missing_creator_gracefully(self):
        srp_link = MagicMock()
        srp_link.creator = None

        with patch(
            target="aasrp.admin.get_main_character_name_from_user", return_value=None
        ):
            result = SrpLinkAdmin._creator(srp_link)

        self.assertIsNone(result)
