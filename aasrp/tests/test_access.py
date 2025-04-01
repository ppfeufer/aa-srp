"""
Testing access to AA-SRP
"""

# Standard Library
from http import HTTPStatus

# Third Party
from faker import Faker

# Django
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

# Alliance Auth (External Libs)
from app_utils.testing import create_fake_user

# AA SRP
from aasrp.models import SrpLink

fake = Faker()


class TestAccess(TestCase):
    """
    Testing access to various views
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()
        cls.group = Group.objects.create(name="Enterprise Crew")

        # User without access
        cls.user_without_access = create_fake_user(
            character_id=1001, character_name="Wesley Crusher"
        )

        # User with basic_access
        cls.user_with_basic_access = create_fake_user(
            character_id=1002,
            character_name="Miles O'Brian",
            permissions=["aasrp.basic_access"],
        )

        # User with create_srp
        cls.user_with_create_srp = create_fake_user(
            character_id=1003,
            character_name="Worf",
            permissions=["aasrp.basic_access", "aasrp.create_srp"],
        )

        # User with manage_srp_requests
        cls.user_with_manage_srp_requests = create_fake_user(
            character_id=1004,
            character_name="James T. Kirk",
            permissions=["aasrp.basic_access", "aasrp.manage_srp_requests"],
        )

        # User with manage_srp
        cls.user_with_manage_srp = create_fake_user(
            character_id=1005,
            character_name="Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )

        cls.defaul_srp_link = SrpLink(
            srp_name="Foobar",
            fleet_time=timezone.now(),
            fleet_doctrine="Ships",
            aar_link="",
            srp_code=get_random_string(length=16),
            fleet_commander=None,
            creator=cls.user_with_create_srp,
        )
        cls.defaul_srp_link.save()

    def test_should_show_dashboard(self):
        """
        Test that a user with basic_access can see the srp module

        :return:
        :rtype:
        """

        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        res = self.client.get(path=reverse("aasrp:srp_links"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_not_show_dashboard(self):
        """
        Test that a user without basic_access can't see the srp module

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_without_access)

        # when
        res = self.client.get(path=reverse("aasrp:srp_links"))

        # then
        self.assertNotEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_should_show_dashboard_with_all_srp_links(self):
        """
        Test that a user with manage_srp can see all srp links

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_manage_srp)

        # when
        res = self.client.get(path=reverse("aasrp:srp_links_all"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_should_not_show_dashboard_with_all_srp_links(self):
        """
        Test that a user without manage_srp can't see all srp links

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_basic_access)

        # when
        res = self.client.get(path=reverse("aasrp:srp_links_all"))

        # then
        self.assertNotEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_srp_link_add_with_create_srp_permission(self):
        """
        Test if a user with create_srp permission can create an SRP link

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_create_srp)

        # when
        res = self.client.get(path=reverse("aasrp:add_srp_link"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_srp_link_add_with_manage_srp_permission(self):
        """
        Test if a user with manage_srp permission can create an SRP link

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_manage_srp)

        # when
        res = self.client.get(path=reverse("aasrp:add_srp_link"))

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_srp_link_add_without_appropriate_permission(self):
        """
        Test that a user with basic_access permission cannot create an SRP link

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_basic_access)

        # when
        res = self.client.get(path=reverse("aasrp:add_srp_link"))

        # then
        self.assertNotEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_srp_link_add_without_permission(self):
        """
        Test that a user without permissions canot create an SRP link

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_without_access)

        # when
        res = self.client.get(path=reverse("aasrp:add_srp_link"))

        # then
        self.assertNotEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_srp_link_edit_with_create_srp_permission(self):
        """
        Test if a user with create_srp permission can edit an SRP link

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_create_srp)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aasrp:edit_srp_link", args=[self.defaul_srp_link.srp_code]
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_srp_link_edit_with_manage_srp_permission(self):
        """
        Test if a user with manage_srp permission can edit an SRP link

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_manage_srp)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aasrp:edit_srp_link", args=[self.defaul_srp_link.srp_code]
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_request_srp_with_basic_access_permission(self):
        """
        Test if a user with basic_access can open the Request SRP view

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_basic_access)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aasrp:request_srp", args=[self.defaul_srp_link.srp_code]
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_request_srp_without_permission(self):
        """
        Test that a user without access cannot open the Request SRP view

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_without_access)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aasrp:request_srp", args=[self.defaul_srp_link.srp_code]
            )
        )

        # then
        self.assertNotEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)

    def test_srp_link_view_requests_with_manage_srp_permission(self):
        """
        Test if a user with manage_srp permission can view srp requests

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_manage_srp)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aasrp:view_srp_requests", args=[self.defaul_srp_link.srp_code]
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_srp_link_view_requests_with_manage_srp_requests_permission(self):
        """
        Test if a user with manage_srp_requests permission can view srp requests

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_manage_srp_requests)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aasrp:view_srp_requests", args=[self.defaul_srp_link.srp_code]
            )
        )

        # then
        self.assertEqual(first=res.status_code, second=HTTPStatus.OK)

    def test_srp_link_view_requests_without_permission(self):
        """
        Test that a user with basic_access permission cannot view srp requests

        :return:
        :rtype:
        """

        # given
        self.client.force_login(user=self.user_with_basic_access)

        # when
        res = self.client.get(
            path=reverse(
                viewname="aasrp:view_srp_requests", args=[self.defaul_srp_link.srp_code]
            )
        )

        # then
        self.assertNotEqual(first=res.status_code, second=HTTPStatus.OK)
        self.assertEqual(first=res.status_code, second=HTTPStatus.FOUND)
