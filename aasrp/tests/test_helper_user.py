"""
Test the helper functions in aasrp/helper/user.py
"""

# Standard Library
from unittest.mock import patch

# Django
from django.contrib.auth.models import User

# AA SRP
from aasrp.helper.user import get_pending_requests_count_for_user, get_user_settings
from aasrp.models import UserSetting
from aasrp.tests import BaseTestCase


class TestGetUserSettings(BaseTestCase):
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


class TestPendingRequestsCount(BaseTestCase):
    """
    Test the get_pending_requests_count_for_user function
    """

    def test_returns_pending_request_count_for_user(self):
        """
        Test that the function returns the correct count of pending requests for a user

        :return:
        :rtype:
        """

        user = User.objects.create_user(username="user1", password="pass")

        with patch(
            "aasrp.models.SrpRequest.pending_requests_count_for_user"
        ) as mock_pending:
            mock_pending.return_value = 5

            result = get_pending_requests_count_for_user(user)

            self.assertEqual(result, 5)
            mock_pending.assert_called_once_with(user=user)

    def test_returns_none_when_no_pending_requests_exist(self):
        """
        Test that the function returns None when there are no pending requests for a user

        :return:
        :rtype:
        """

        user = User.objects.create_user(username="user2", password="pass")

        with patch(
            "aasrp.models.SrpRequest.pending_requests_count_for_user"
        ) as mock_pending:
            mock_pending.return_value = None

            result = get_pending_requests_count_for_user(user)

            self.assertIsNone(result)
            mock_pending.assert_called_once_with(user=user)
