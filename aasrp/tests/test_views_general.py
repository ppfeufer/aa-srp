"""
Tests for aasrp/views/general.py
"""

# Standard Library
from http import HTTPStatus
from unittest.mock import MagicMock, patch

# Third Party
from eve_sde.models import ItemType

# Django
from django.contrib.auth.models import Permission, User
from django.test import Client
from django.urls import reverse
from django.utils import timezone

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils

# AA SRP
from aasrp.models import Setting, SrpLink, SrpRequest, UserSetting
from aasrp.tests import BaseTestCase
from aasrp.tests.utils import create_fake_user
from aasrp.views.general import _save_srp_request


class BaseViewsTestCase(BaseTestCase):
    """
    Base test case for views tests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up a SrpLink instance for testing.

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


class TestViewOwnRequests(BaseViewsTestCase):
    """
    Test the view_own_requests view.
    """

    def test_redirects_unauthenticated_user(self):
        """
        Test that an unauthenticated user is redirected to the login page when trying to access the view_own_requests view.

        :return:
        :rtype:
        """

        response = self.client.get(reverse("aasrp:own_srp_requests"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_renders_template_for_authenticated_user(self):
        """
        Test that an authenticated user can access the view_own_requests view and the correct template is used.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_jean_luc_picard)

        response = self.client.get(reverse("aasrp:own_srp_requests"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "aasrp/view-own-requests.html")


class TestUserSettingsView(BaseViewsTestCase):
    def test_renders_user_settings_template_for_authenticated_user(self):
        """
        Test that an authenticated user can access the user_settings view and the correct template is used.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_wesley_crusher)
        response = self.client.get(reverse("aasrp:user_settings"))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "aasrp/user-settings.html")

    def test_redirects_unauthenticated_user_to_login(self):
        """
        Test that an unauthenticated user is redirected to the login page when trying to access the user_settings view.

        :return:
        :rtype:
        """

        response = self.client.get(reverse("aasrp:user_settings"))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn("/login/", response.url)

    def test_saves_valid_user_settings_form(self):
        """
        Test that a valid user settings form is saved correctly.

        :return:
        :rtype:
        """

        user = self.user_wesley_crusher
        self.client.force_login(user)

        user_settings = UserSetting.objects.create(
            user=user, disable_notifications=False
        )
        form_data = {"disable_notifications": "on"}
        response = self.client.post(reverse("aasrp:user_settings"), data=form_data)
        user_settings.refresh_from_db()

        self.assertEqual(user_settings.disable_notifications, True)
        self.assertRedirects(response, reverse("aasrp:user_settings"))

    def test_does_not_save_invalid_user_settings_form(self):
        """
        Test that an invalid user settings form does not change the settings.

        :return:
        :rtype:
        """

        user = self.user_wesley_crusher
        self.client.force_login(user)

        user_settings = UserSetting.objects.create(
            user=user, disable_notifications=False
        )
        form_data = {}  # Checkbox omitted
        response = self.client.post(reverse("aasrp:user_settings"), data=form_data)
        user_settings.refresh_from_db()

        self.assertEqual(user_settings.disable_notifications, False)
        self.assertRedirects(response, reverse("aasrp:user_settings"))


class TestSrpLinkAddView(BaseTestCase):
    """
    Tests for the srp_link_add view.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the srp_link_add view tests.

        :return:
        :rtype:
        """

        cls.user = AuthUtils.create_user("test_user")

        AuthUtils.add_permission_to_user_by_name("aasrp.basic_access", cls.user)
        AuthUtils.add_permission_to_user_by_name("aasrp.create_srp", cls.user)
        AuthUtils.add_main_character_2(
            cls.user, name="Test Character", character_id=123456
        )

    def setUp(self):
        """
        Set up the test client and log in the test user.
        :return:
        :rtype:
        """

        self.client = Client()
        self.client.force_login(self.user)

    def test_srp_link_add_get_renders(self):
        """
        Test that the add SRP link GET view renders correctly.

        :return:
        :rtype:
        """

        response = self.client.get(reverse("aasrp:add_srp_link"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "aasrp/link-add.html")

    def test_srp_link_add_post_valid(self):
        """
        Test that a valid POST creates a new SRP link.

        :return:
        :rtype:
        """

        response = self.client.post(
            reverse("aasrp:add_srp_link"),
            data={
                "srp_name": "Test Fleet",
                "fleet_time": "2024-01-01 12:00:00",
                "fleet_doctrine": "Test Doctrine",
                "aar_link": "",
            },
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))
        self.assertTrue(SrpLink.objects.filter(srp_name="Test Fleet").exists())

    def test_srp_link_add_post_invalid(self):
        """
        Test that an invalid POST does not create a new SRP link and re-renders the form with errors.

        :return:
        :rtype:
        """

        response = self.client.post(
            reverse("aasrp:add_srp_link"),
            data={},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "aasrp/link-add.html")

    def test_srp_link_add_requires_permission(self):
        """
        Test that adding an SRP link requires the create_srp permission.

        :return:
        :rtype:
        """

        user_no_perm = AuthUtils.create_user("user_no_perm")
        AuthUtils.add_permission_to_user_by_name("aasrp.basic_access", user_no_perm)
        self.client.force_login(user_no_perm)

        response = self.client.get(reverse("aasrp:add_srp_link"))

        self.assertNotEqual(response.status_code, 200)


class TestSrpLinkEditView(BaseTestCase):
    """
    Tests for the srp_link_edit view.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the srp_link_edit view tests.

        :return:
        :rtype:
        """

        cls.user = AuthUtils.create_user("test_user")

        AuthUtils.add_permission_to_user_by_name("aasrp.basic_access", cls.user)
        AuthUtils.add_permission_to_user_by_name("aasrp.create_srp", cls.user)
        AuthUtils.add_main_character_2(
            cls.user, name="Test Character", character_id=123456
        )

        cls.srp_link = SrpLink.objects.create(
            srp_name="Test Fleet",
            fleet_time="2024-01-01 12:00:00",
            fleet_doctrine="Test Doctrine",
            srp_code="TESTCODE1234",
            creator=cls.user,
        )

    def setUp(self):
        """
        Set up the test client and log in the test user.

        :return:
        :rtype:
        """

        self.client = Client()
        self.client.force_login(self.user)

    def test_srp_link_edit_get_renders(self):
        """
        Test that the edit SRP link GET view renders correctly.

        :return:
        :rtype:
        """

        response = self.client.get(
            reverse("aasrp:edit_srp_link", args=[self.srp_link.srp_code])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "aasrp/link-edit.html")

    def test_srp_link_edit_invalid_code_redirects(self):
        """
        Test that an invalid SRP code redirects with an error.

        :return:
        :rtype:
        """

        response = self.client.get(reverse("aasrp:edit_srp_link", args=["INVALIDCODE"]))

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_srp_link_edit_post_valid(self):
        """
        Test that a valid POST updates the SRP link.

        :return:
        :rtype:
        """

        response = self.client.post(
            reverse("aasrp:edit_srp_link", args=[self.srp_link.srp_code]),
            data={"aar_link": "https://example.com/aar"},
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))
        self.srp_link.refresh_from_db()
        self.assertEqual(self.srp_link.aar_link, "https://example.com/aar")


class TestCompleteSrpLinkView(BaseTestCase):
    """
    Tests for the complete_srp_link view.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the complete_srp_link view tests.

        :return:
        :rtype:
        """

        cls.user = AuthUtils.create_user("test_user")

        AuthUtils.add_permission_to_user_by_name("aasrp.manage_srp", cls.user)
        AuthUtils.add_main_character_2(
            cls.user, name="Test Character", character_id=123456
        )

        cls.srp_link = SrpLink.objects.create(
            srp_name="Test Fleet",
            fleet_time="2024-01-01 12:00:00",
            fleet_doctrine="Test Doctrine",
            srp_code="TESTCODE5678",
            creator=cls.user,
        )

    def setUp(self):
        """
        Set up the test client and log in the test user.

        :return:
        :rtype:
        """

        self.client = Client()
        self.client.force_login(self.user)

    def test_complete_srp_link(self):
        """
        Test that an SRP link can be marked as complete.

        :return:
        :rtype:
        """

        self.client.force_login(self.user)  # ensure user is logged in
        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
            Permission.objects.get(
                codename="manage_srp", content_type__app_label="aasrp"
            ),
        )

        response = self.client.get(
            reverse("aasrp:complete_srp_link", args=[self.srp_link.srp_code])
        )

        self.assertRedirects(
            response,
            reverse("aasrp:srp_links"),
        )

        self.srp_link.refresh_from_db()
        self.assertEqual(self.srp_link.srp_status, SrpLink.Status.COMPLETED)

    def test_complete_srp_link_invalid_code(self):
        """
        Test that an invalid SRP code redirects with an error.

        :return:
        :rtype:
        """

        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
            Permission.objects.get(
                codename="manage_srp", content_type__app_label="aasrp"
            ),
        )
        response = self.client.get(
            reverse("aasrp:complete_srp_link", args=["INVALID_CODE"])
        )
        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_complete_srp_link_requires_manage_srp(self):
        """
        Test that marking an SRP link as complete requires the manage_srp permission.

        :return:
        :rtype:
        """

        user_no_perm = AuthUtils.create_user("user_no_manage")
        AuthUtils.add_permission_to_user_by_name("aasrp.basic_access", user_no_perm)
        self.client.force_login(user_no_perm)

        response = self.client.get(
            reverse("aasrp:complete_srp_link", args=[self.srp_link.srp_code])
        )

        self.assertNotEqual(response.status_code, 200)


class TestEnableDisableSrpLinkViews(BaseTestCase):
    """
    Tests for the enable_srp_link and disable_srp_link views.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the enable_srp_link and disable_srp_link view tests.

        :return:
        :rtype:
        """

        cls.user = AuthUtils.create_user("test_user")

        AuthUtils.add_permission_to_user_by_name("aasrp.manage_srp", cls.user)
        AuthUtils.add_main_character_2(
            cls.user, name="Test Character", character_id=123456
        )

        cls.srp_link = SrpLink.objects.create(
            srp_name="Test Fleet",
            fleet_time="2024-01-01 12:00:00",
            fleet_doctrine="Test Doctrine",
            srp_code="ENABLETEST01",
            creator=cls.user,
        )

    def setUp(self):
        """
        Set up the test client and log in the test user.

        :return:
        :rtype:
        """

        self.client = Client()
        self.client.force_login(self.user)

    def test_enable_srp_link(self):
        """
        Test that an SRP link can be enabled.

        :return:
        :rtype:
        """

        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
            Permission.objects.get(
                codename="manage_srp", content_type__app_label="aasrp"
            ),
        )

        self.srp_link.srp_status = SrpLink.Status.CLOSED
        self.srp_link.save()

        response = self.client.get(
            reverse("aasrp:enable_srp_link", args=[self.srp_link.srp_code])
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))
        self.srp_link.refresh_from_db()
        self.assertEqual(self.srp_link.srp_status, SrpLink.Status.ACTIVE)

    def test_disable_srp_link(self):
        """
        Test that an SRP link can be disabled.

        :return:
        :rtype:
        """

        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
            Permission.objects.get(
                codename="manage_srp", content_type__app_label="aasrp"
            ),
        )

        response = self.client.get(
            reverse("aasrp:disable_srp_link", args=[self.srp_link.srp_code])
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))
        self.srp_link.refresh_from_db()
        self.assertEqual(self.srp_link.srp_status, SrpLink.Status.CLOSED)

    def test_enable_srp_link_invalid_code(self):
        """
        Test that enabling an invalid SRP link shows an error.

        :return:
        :rtype:
        """

        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
            Permission.objects.get(
                codename="manage_srp", content_type__app_label="aasrp"
            ),
        )

        response = self.client.get(
            reverse("aasrp:enable_srp_link", args=["INVALIDCODE"])
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_disable_srp_link_invalid_code(self):
        """
        Test that disabling an invalid SRP link shows an error.

        :return:
        :rtype:
        """

        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
            Permission.objects.get(
                codename="manage_srp", content_type__app_label="aasrp"
            ),
        )

        response = self.client.get(
            reverse("aasrp:disable_srp_link", args=["INVALIDCODE"])
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))


class TestDeleteSrpLinkView(BaseTestCase):
    """
    Tests for the delete_srp_link view.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the delete_srp_link view tests.

        :return:
        :rtype:
        """

        cls.user = AuthUtils.create_user("test_user")

        AuthUtils.add_permission_to_user_by_name("aasrp.manage_srp", cls.user)
        AuthUtils.add_main_character_2(
            cls.user, name="Test Character", character_id=123456
        )

    def setUp(self):
        """
        Set up the test client and log in the test user.

        :return:
        :rtype:
        """

        self.client = Client()
        self.client.force_login(self.user)

        self.srp_link = SrpLink.objects.create(
            srp_name="Test Fleet",
            fleet_time="2024-01-01 12:00:00",
            fleet_doctrine="Test Doctrine",
            srp_code="DELETETEST01",
            creator=self.user,
        )

    def test_delete_srp_link(self):
        """
        Test that an SRP link can be deleted.

        :return:
        :rtype:
        """

        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
            Permission.objects.get(
                codename="manage_srp", content_type__app_label="aasrp"
            ),
        )

        response = self.client.get(
            reverse("aasrp:delete_srp_link", args=[self.srp_link.srp_code])
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))
        self.assertFalse(
            SrpLink.objects.filter(srp_code=self.srp_link.srp_code).exists()
        )

    def test_delete_srp_link_invalid_code(self):
        """
        Test that deleting an SRP link with an invalid code redirects with an error.

        :return:
        :rtype:
        """

        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
            Permission.objects.get(
                codename="manage_srp", content_type__app_label="aasrp"
            ),
        )

        response = self.client.get(
            reverse("aasrp:delete_srp_link", args=["INVALIDCODE"])
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_delete_srp_link_requires_manage_srp(self):
        """
        Test that deleting an SRP link requires the manage_srp permission.

        :return:
        :rtype:
        """

        user_no_perm = AuthUtils.create_user("user_no_delete")
        AuthUtils.add_permission_to_user_by_name("aasrp.basic_access", user_no_perm)
        self.client.force_login(user_no_perm)

        response = self.client.get(
            reverse("aasrp:delete_srp_link", args=[self.srp_link.srp_code])
        )

        self.assertNotEqual(response.status_code, 200)


class TestSrpLinkViewRequestsView(BaseTestCase):
    """
    Tests for the srp_link_view_requests view.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the srp_link_view_requests view tests.

        :return:
        :rtype:
        """

        cls.user = AuthUtils.create_user("test_user")

        AuthUtils.add_permission_to_user_by_name("aasrp.manage_srp", cls.user)
        AuthUtils.add_main_character_2(
            cls.user, name="Test Character", character_id=123456
        )

        cls.srp_link = SrpLink.objects.create(
            srp_name="Test Fleet",
            fleet_time="2024-01-01 12:00:00",
            fleet_doctrine="Test Doctrine",
            srp_code="VIEWREQTEST1",
            creator=cls.user,
        )

    def setUp(self):
        """
        Set up the test client and log in the test user.

        :return:
        :rtype:
        """

        self.client = Client()
        self.client.force_login(self.user)

    def test_view_srp_requests_renders(self):
        """
        Test that the view SRP requests view renders correctly.

        :return:
        :rtype:
        """

        response = self.client.get(
            reverse("aasrp:view_srp_requests", args=[self.srp_link.srp_code])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "aasrp/view-requests.html")

    def test_view_srp_requests_context(self):
        """
        Test that the view SRP requests view context contains the expected data.

        :return:
        :rtype:
        """

        response = self.client.get(
            reverse("aasrp:view_srp_requests", args=[self.srp_link.srp_code])
        )

        self.assertIn("srp_link", response.context)
        self.assertIn("forms", response.context)
        self.assertIn("reject_request", response.context["forms"])
        self.assertIn("accept_request", response.context["forms"])
        self.assertIn("accept_rejected_request", response.context["forms"])

    def test_view_srp_requests_invalid_code_redirects(self):
        """
        Test that an invalid SRP code redirects with an error.

        :return:
        :rtype:
        """

        self.user.user_permissions.add(
            Permission.objects.get(
                codename="basic_access", content_type__app_label="aasrp"
            ),
        )

        response = self.client.get(
            reverse("aasrp:view_srp_requests", args=["INVALIDCODE"])
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_view_srp_requests_requires_permission(self):
        """
        Test that viewing SRP requests requires the manage_srp permission.

        :return:
        :rtype:
        """

        user_no_perm = AuthUtils.create_user("user_no_viewreq")
        AuthUtils.add_permission_to_user_by_name("aasrp.basic_access", user_no_perm)
        self.client.force_login(user_no_perm)

        response = self.client.get(
            reverse("aasrp:view_srp_requests", args=[self.srp_link.srp_code])
        )

        self.assertNotEqual(response.status_code, 200)


class TestRequestSrpView(BaseTestCase):
    """
    Tests for the request_srp view.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the request_srp view tests.

        :return:
        :rtype:
        """

        cls.user = AuthUtils.create_user("test_user")

        AuthUtils.add_permission_to_user_by_name("aasrp.basic_access", cls.user)
        AuthUtils.add_main_character_2(
            cls.user, name="Test Character", character_id=123456
        )

        cls.srp_link = SrpLink.objects.create(
            srp_name="Test Fleet",
            fleet_time="2024-01-01 12:00:00",
            fleet_doctrine="Test Doctrine",
            srp_code="REQSRPTEST01",
            srp_status=SrpLink.Status.ACTIVE,
            creator=cls.user,
        )

        cls.closed_srp_link = SrpLink.objects.create(
            srp_name="Closed Fleet",
            fleet_time="2024-01-01 12:00:00",
            fleet_doctrine="Test Doctrine",
            srp_code="CLOSEDSRP001",
            srp_status=SrpLink.Status.CLOSED,
            creator=cls.user,
        )

    def setUp(self):
        """
        Set up the test client and log in the test user.

        :return:
        :rtype:
        """

        self.client = Client()
        self.client.force_login(self.user)

    def test_request_srp_get_renders(self):
        """
        Test that the request SRP GET view renders correctly.

        :return:
        :rtype:
        """

        response = self.client.get(
            reverse("aasrp:request_srp", args=[self.srp_link.srp_code])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "aasrp/request-srp.html")

    def test_request_srp_invalid_code_redirects(self):
        """
        Test that an invalid SRP code redirects with an error.

        :return:
        :rtype:
        """

        response = self.client.get(reverse("aasrp:request_srp", args=["INVALIDCODE"]))

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_request_srp_closed_link_redirects(self):
        """
        Test that trying to request an SRP for a closed link redirects with an error.

        :return:
        :rtype:
        """

        response = self.client.get(
            reverse("aasrp:request_srp", args=[self.closed_srp_link.srp_code])
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_request_srp_requires_login(self):
        """
        Test that requesting an SRP requires the user to be logged in.

        :return:
        :rtype:
        """

        self.client.logout()

        response = self.client.get(
            reverse("aasrp:request_srp", args=[self.srp_link.srp_code])
        )

        self.assertNotEqual(response.status_code, 200)


class TestSaveSrpRequest(BaseTestCase):
    """
    Tests for the _save_srp_request function.
    """

    def setUp(self):
        """
        Set up common test data for the _save_srp_request tests.
        :return:
        :rtype:
        """

        # use a real User instance so RequestComment.creator accepts it
        self.user = User.objects.create_user(
            username="save_srp_user", password="password"
        )
        self.request = MagicMock(user=self.user)
        self.srp_link = MagicMock(srp_name="Test Fleet", srp_code="TESTCODE")
        self.killmail_link = "https://zkillboard.com/kill/12345678/"
        self.ship_type_id = 123
        self.ship_value = 1000000
        self.victim_id = 456
        self.additional_info = "Test additional info"

    @patch("aasrp.views.general.EveCharacter.objects.get_character_by_id")
    @patch("aasrp.views.general.ItemType.objects.get")
    @patch("aasrp.views.general.SrpRequest.objects.create")
    @patch("aasrp.views.general.RequestComment.objects.bulk_create")
    @patch("aasrp.views.general.SrpRequest.objects.get_insurance_for_ship_type")
    @patch("aasrp.views.general.Insurance.objects.bulk_create")
    def test_saves_valid_srp_request(
        self,
        mock_insurance_bulk_create,
        mock_get_insurance,
        mock_comment_bulk_create,
        mock_srp_request_create,
        mock_item_type_get,
        mock_get_character_by_id,
    ):
        """
        Test that a valid SRP request is saved correctly.

        :param mock_insurance_bulk_create:
        :type mock_insurance_bulk_create:
        :param mock_get_insurance:
        :type mock_get_insurance:
        :param mock_comment_bulk_create:
        :type mock_comment_bulk_create:
        :param mock_srp_request_create:
        :type mock_srp_request_create:
        :param mock_item_type_get:
        :type mock_item_type_get:
        :param mock_get_character_by_id:
        :type mock_get_character_by_id:
        :return:
        :rtype:
        """

        mock_character = MagicMock()
        mock_get_character_by_id.return_value = mock_character

        mock_ship = MagicMock(name="Test Ship")
        mock_item_type_get.return_value = mock_ship

        srp_request_instance = SrpRequest()
        mock_srp_request_create.return_value = srp_request_instance

        mock_insurance = MagicMock()
        mock_get_insurance.return_value.levels = [mock_insurance]

        result = _save_srp_request(
            request=self.request,
            srp_link=self.srp_link,
            killmail_link=self.killmail_link,
            ship_type_id=self.ship_type_id,
            ship_value=self.ship_value,
            victim_id=self.victim_id,
            additional_info=self.additional_info,
        )

        self.assertEqual(result, srp_request_instance)
        mock_get_character_by_id.assert_called_once_with(character_id=self.victim_id)
        mock_item_type_get.assert_called_once_with(id=self.ship_type_id)
        mock_srp_request_create.assert_called_once()
        mock_comment_bulk_create.assert_called_once()
        mock_get_insurance.assert_called_once_with(ship_type_id=self.ship_type_id)
        mock_insurance_bulk_create.assert_called_once()

    @patch("aasrp.views.general.EveCharacter.objects.get_character_by_id")
    def test_raises_error_for_invalid_character(self, mock_get_character_by_id):
        """
        Test that an invalid character ID raises an error.

        :param mock_get_character_by_id:
        :type mock_get_character_by_id:
        :return:
        :rtype:
        """

        mock_get_character_by_id.side_effect = EveCharacter.DoesNotExist

        with self.assertRaises(EveCharacter.DoesNotExist):
            _save_srp_request(
                request=self.request,
                srp_link=self.srp_link,
                killmail_link=self.killmail_link,
                ship_type_id=self.ship_type_id,
                ship_value=self.ship_value,
                victim_id=self.victim_id,
                additional_info=self.additional_info,
            )

    @patch("aasrp.views.general.ItemType.objects.get")
    def test_raises_error_for_invalid_ship_type(self, mock_item_type_get):
        """
        Test that an invalid ship type ID raises an error.

        :param mock_item_type_get:
        :type mock_item_type_get:
        :return:
        :rtype:
        """

        mock_item_type_get.side_effect = ItemType.DoesNotExist

        with self.assertRaises(ItemType.DoesNotExist):
            _save_srp_request(
                request=self.request,
                srp_link=self.srp_link,
                killmail_link=self.killmail_link,
                ship_type_id=self.ship_type_id,
                ship_value=self.ship_value,
                victim_id=self.victim_id,
                additional_info=self.additional_info,
            )


class TestRequestSrp(BaseViewsTestCase):
    """
    Tests for the request_srp view.
    """

    def setUp(self):
        """
        Set up common test data for the request_srp view tests.

        :return:
        :rtype:
        """

        self.user = self.user_wesley_crusher
        self.client.force_login(self.user)

        self.srp_link = SrpLink.objects.create(
            srp_name="Test Fleet",
            srp_code="TESTCODE",
            srp_status=SrpLink.Status.ACTIVE,
            creator=self.user,
            fleet_time=timezone.now(),
        )
        self.url = reverse("aasrp:request_srp", args=[self.srp_link.srp_code])

    @patch("aasrp.managers.SrpRequestManager.get_kill_id")
    @patch("aasrp.managers.SrpRequestManager.get_kill_data")
    @patch("aasrp.views.general._save_srp_request")
    @patch("aasrp.views.general.notify_srp_team")
    def test_saves_valid_srp_request(
        self,
        mock_notify_srp_team,
        mock_save_srp_request,
        mock_get_kill_data,
        mock_get_kill_id,
    ):
        """
        Test that a valid SRP request is saved correctly through the request_srp view.

        :param mock_notify_srp_team:
        :type mock_notify_srp_team:
        :param mock_save_srp_request:
        :type mock_save_srp_request:
        :param mock_get_kill_data:
        :type mock_get_kill_data:
        :param mock_get_kill_id:
        :type mock_get_kill_id:
        :return:
        :rtype:
        """

        # Get or create the singleton Setting instance
        setting = Setting.get_solo()
        setting.loss_value_source = "totalValue"
        setting.save()

        mock_get_kill_id.return_value = 12345678
        mock_get_kill_data.return_value = {
            "victim_id": 456,
            "ship_type_id": 123,
            "ship_value": 1000000,
        }

        victim_char = EveCharacter.objects.create(
            character_id=456,
            character_name="Victim Character",
            corporation_id=789,
            corporation_name="Victim Corp",
        )
        self.user.character_ownerships.create(character=victim_char)
        self.user.profile.main_character = victim_char
        self.user.profile.save()

        mock_save_srp_request.return_value = MagicMock()

        response = self.client.post(
            self.url,
            {
                "killboard_link": "https://zkillboard.com/kill/12345678/",
                "additional_info": "Test additional info",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("aasrp:srp_links"))
        # Called twice: once in form validation, once in view
        self.assertEqual(mock_get_kill_id.call_count, 2)
        mock_get_kill_data.assert_called_once()
        mock_save_srp_request.assert_called_once()
        mock_notify_srp_team.assert_called_once()

    @patch("aasrp.models.SrpRequest.objects.get_kill_id")
    @patch("aasrp.models.SrpRequest.objects.get_kill_data")
    def test_shows_error_when_character_not_owned(
        self, mock_get_kill_data, mock_get_kill_id
    ):
        """
        Test that a killmail not involving the user's character shows an error message.

        :param mock_get_kill_data:
        :type mock_get_kill_data:
        :param mock_get_kill_id:
        :type mock_get_kill_id:
        :return:
        :rtype:
        """

        mock_get_kill_id.return_value = "kill_id_123"
        mock_get_kill_data.return_value = {
            "victim_id": 1,
            "ship_value": "1000000",
            "ship_type_id": 99999,
        }
        form_data = {
            "killboard_link": "https://zkillboard.com/kill/128743453/",
            "additional_info": "Test info",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_redirects_for_invalid_srp_code(self):
        """
        Test that accessing the request_srp view with an invalid SRP code redirects with an error.

        :return:
        :rtype:
        """

        invalid_url = reverse("aasrp:request_srp", args=["INVALIDCODE"])

        response = self.client.get(invalid_url)

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_redirects_for_inactive_srp_link(self):
        """
        Test that accessing the request_srp view for an inactive SRP link redirects with an error.

        :return:
        :rtype:
        """

        self.srp_link.srp_status = SrpLink.Status.CLOSED
        self.srp_link.save()

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    @patch("aasrp.form.SrpRequest.objects.get_kill_id")
    def test_handles_invalid_killmail(self, mock_get_kill_id):
        """
        Test that submitting a killmail that cannot be parsed shows form errors.

        :return:
        :rtype:
        """

        mock_get_kill_id.side_effect = ValueError("Invalid killmail")

        response = self.client.post(
            self.url,
            {
                "killboard_link": "https://zkillboard.com/kill/12345/",
                "additional_info": "Test info",
            },
        )

        # Should re-render the form with errors, not redirect
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(
            response.context["form"], "killboard_link", "Invalid killmail"
        )

    @patch("aasrp.views.general.SrpRequest.objects.get_kill_data")
    @patch("aasrp.views.general.SrpRequest.objects.get_kill_id")
    def test_handles_invalid_killmail_in_view(
        self, mock_get_kill_id, mock_get_kill_data
    ):
        """
        Test that if the killmail is valid enough to get an ID but fails when fetching data, it shows an error message.

        :param mock_get_kill_id:
        :type mock_get_kill_id:
        :param mock_get_kill_data:
        :type mock_get_kill_data:
        :return:
        :rtype:
        """

        mock_get_kill_id.return_value = "12345"
        mock_get_kill_data.side_effect = ValueError("API error")

        response = self.client.post(
            self.url,
            {
                "killboard_link": "https://zkillboard.com/kill/12345/",
                "additional_info": "Test info",
            },
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))

    def test_rejects_request_for_unowned_character(self):
        """
        Test that submitting a killmail for a character not owned by the user redirects with an error.

        :return:
        :rtype:
        """

        response = self.client.post(
            self.url,
            {
                "killboard_link": "https://zkillboard.com/kill/12345678/",
                "additional_info": "Test additional info",
            },
        )

        self.assertRedirects(response, reverse("aasrp:srp_links"))
