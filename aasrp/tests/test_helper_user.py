"""
Test the helper functions in aasrp/helper/user.py
"""

# Django
from django.contrib.auth.models import User
from django.test import TestCase

# AA SRP
from aasrp.helper.user import get_user_settings
from aasrp.models import UserSetting


class TestGetUserSettings(TestCase):
    """
    Test the get_user_settings function
    """

    def test_get_user_settings_creates_new_settings_for_new_user(self):
        """
        Test that get_user_settings creates new settings for a new user

        :return:
        :rtype:
        """

        user = User.objects.create(username="newuser")
        user_settings = get_user_settings(user)

        self.assertIsInstance(user_settings, UserSetting)
        self.assertEqual(user_settings.user, user)

    def test_get_user_settings_returns_existing_settings_for_existing_user(self):
        """
        Test that get_user_settings returns existing settings for an existing user

        :return:
        :rtype:
        """

        user = User.objects.create(username="existinguser")
        existing_settings = UserSetting.objects.create(user=user)
        user_settings = get_user_settings(user)

        self.assertEqual(user_settings, existing_settings)

    def test_get_user_settings_handles_multiple_calls_for_same_user(self):
        """
        Test that get_user_settings handles multiple calls for the same user

        :return:
        :rtype:
        """

        user = User.objects.create(username="repeateduser")
        first_call_settings = get_user_settings(user)
        second_call_settings = get_user_settings(user)

        self.assertEqual(first_call_settings, second_call_settings)
