"""
Test auth_hooks
"""

# Standard Library
from http import HTTPStatus
from unittest.mock import Mock, patch

# Django
from django.test import TestCase
from django.urls import reverse

# AA SRP
from aasrp import __title__
from aasrp.auth_hooks import AaSrpMenuItem, register_menu
from aasrp.tests.utils import create_fake_user


class TestMenuItemHtml(TestCase):
    """
    Test the HTML of the menu item
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()

        # User cannot access
        cls.user_1001 = create_fake_user(
            character_id=1001, character_name="Peter Parker"
        )

        # User can access
        cls.user_1002 = create_fake_user(
            character_id=1002,
            character_name="Bruce Wayne",
            permissions=["aasrp.basic_access"],
        )

        cls.html_menu = f"""
            <li class="d-flex flex-wrap m-2 p-2 pt-0 pb-0 mt-0 mb-0 me-0 pe-0">
                <i class="nav-link fa-regular fa-money-bill-1 fa-fw align-self-center me-3 "></i>
                <a class="nav-link flex-fill align-self-center me-auto" href="{reverse('aasrp:srp_links')}">
                    {__title__}
                </a>
            </li>
        """

    def test_render_hook_success(self):
        """
        Test should show the link to the app in the navigation to user with access

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_1002)

        response = self.client.get(path=reverse(viewname="authentication:dashboard"))

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertContains(response=response, text=self.html_menu, html=True)

    def test_render_hook_fail(self):
        """
        Test should not show the link to the app in the
        navigation to user without access

        :return:
        :rtype:
        """

        self.client.force_login(user=self.user_1001)

        response = self.client.get(path=reverse(viewname="authentication:dashboard"))

        self.assertEqual(first=response.status_code, second=HTTPStatus.OK)
        self.assertNotContains(response=response, text=self.html_menu, html=True)


class TestAaSrpMenuItem(TestCase):
    """
    Test the menu item
    """

    def setUp(self):
        """
        Set up the test

        :return:
        :rtype:
        """

        self.request = Mock()
        self.request.path = reverse(viewname="authentication:dashboard")
        self.menu_item = AaSrpMenuItem()

    def test_render_no_permission(self):
        """
        Test should return empty string if user has no permission

        :return:
        :rtype:
        """

        self.request.user.has_perm.return_value = False
        result = self.menu_item.render(self.request)

        self.assertEqual(result, "")

    @patch("aasrp.auth_hooks.SrpRequest.objects.pending_requests_count_for_user")
    def test_render_with_permission(self, mock_pending_requests):
        """
        Test should return html if a user has permission

        :param mock_pending_requests:
        :type mock_pending_requests:
        :return:
        :rtype:
        """

        self.request.user.has_perm.return_value = True
        mock_pending_requests.return_value = 5
        result = self.menu_item.render(self.request)

        self.assertIsInstance(result, str)


class TestRegisterMenu(TestCase):
    """
    Test register menu
    """

    def test_register_menu(self):
        """
        Test should return menu item

        :return:
        :rtype:
        """

        result = register_menu()

        self.assertIsInstance(result, AaSrpMenuItem)
