"""
Testing access to AA-SRP
"""

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
from aasrp.models import AaSrpLink

fake = Faker()


class TestAccess(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up groups and users
        """

        super().setUpClass()
        cls.group = Group.objects.create(name="Enterprise Crew")

        # User without access
        cls.user_without_access = create_fake_user(1001, "Wesley Crusher")

        # User with basic_access
        cls.user_with_basic_access = create_fake_user(
            1002, "Miles O'Brian", permissions=["aasrp.basic_access"]
        )

        # User with create_srp
        cls.user_with_create_srp = create_fake_user(
            1003, "Worf", permissions=["aasrp.basic_access", "aasrp.create_srp"]
        )

        # User with manage_srp_requests
        cls.user_with_manage_srp_requests = create_fake_user(
            1004,
            "James T. Kirk",
            permissions=["aasrp.basic_access", "aasrp.manage_srp_requests"],
        )

        # User with manage_srp
        cls.user_with_manage_srp = create_fake_user(
            1005,
            "Jean Luc Picard",
            permissions=["aasrp.basic_access", "aasrp.manage_srp"],
        )

    def test_should_show_dashboard(self):
        """
        Test that a user with basic_access can see the srp module
        :return:
        :rtype:
        """

        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        res = self.client.get(reverse("aasrp:dashboard"))

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_not_show_dashboard(self):
        """
        Test that a user without basic_access can't see the srp module
        :return:
        :rtype:
        """

        # given
        self.client.force_login(self.user_without_access)

        # when
        res = self.client.get(reverse("aasrp:dashboard"))

        # then
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 302)

    def test_should_show_dashboard_with_all_srp_links(self):
        """
        Test that a user with manage_srp can see all srp links
        :return:
        :rtype:
        """

        # given
        self.client.force_login(self.user_with_manage_srp)

        # when
        res = self.client.get(reverse("aasrp:all"))

        # then
        self.assertEqual(res.status_code, 200)

    def test_should_not_show_dashboard_with_all_srp_links(self):
        """
        Test that a user without manage_srp can't see all srp links
        :return:
        :rtype:
        """

        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        res = self.client.get(reverse("aasrp:all"))

        # then
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 302)

    def test_srp_link_add_with_create_srp_permission(self):
        """
        Test if a user with create_srp permission can create an SRP link
        :return:
        """

        # given
        self.client.force_login(self.user_with_create_srp)

        # when
        res = self.client.get(reverse("aasrp:add_srp_link"))

        # then
        self.assertEqual(res.status_code, 200)

    def test_srp_link_add_with_manage_srp_permission(self):
        """
        Test if a user with manage_srp permission can create an SRP link
        :return:
        """

        # given
        self.client.force_login(self.user_with_manage_srp)

        # when
        res = self.client.get(reverse("aasrp:add_srp_link"))

        # then
        self.assertEqual(res.status_code, 200)

    def test_srp_link_add_without_appropriate_permission(self):
        """
        Test that a user with basic_access permission cannot create an SRP link
        :return:
        """

        # given
        self.client.force_login(self.user_with_basic_access)

        # when
        res = self.client.get(reverse("aasrp:add_srp_link"))

        # then
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 302)

    def test_srp_link_add_without_permission(self):
        """
        Test that a user without permissions canot create an SRP link
        :return:
        """

        # given
        self.client.force_login(self.user_without_access)

        # when
        res = self.client.get(reverse("aasrp:add_srp_link"))

        # then
        self.assertNotEqual(res.status_code, 200)
        self.assertEqual(res.status_code, 302)

    def test_srp_link_edit_with_create_srp_permission(self):
        """
        Test if a user with create_srp permission can edit an SRP link
        :return:
        """

        # given
        srp_code = get_random_string(length=16)
        srp_link = AaSrpLink(
            srp_name="Foobar",
            fleet_time=timezone.now(),
            fleet_doctrine="Ships",
            aar_link="",
            srp_code=srp_code,
            fleet_commander=None,
            creator=self.user_with_create_srp,
        )
        srp_link.save()

        self.client.force_login(self.user_with_create_srp)

        # when
        res = self.client.get(reverse("aasrp:edit_srp_link", args=[srp_code]))

        # then
        self.assertEqual(res.status_code, 200)

    def test_srp_link_edit_with_manage_srp_permission(self):
        """
        Test if a user with manage_srp permission can edit an SRP link
        :return:
        """

        # given
        srp_code = get_random_string(length=16)
        srp_link = AaSrpLink(
            srp_name="Foobar",
            fleet_time=timezone.now(),
            fleet_doctrine="Ships",
            aar_link="",
            srp_code=srp_code,
            fleet_commander=None,
            creator=self.user_with_create_srp,
        )
        srp_link.save()

        self.client.force_login(self.user_with_manage_srp)

        # when
        res = self.client.get(reverse("aasrp:edit_srp_link", args=[srp_code]))

        # then
        self.assertEqual(res.status_code, 200)