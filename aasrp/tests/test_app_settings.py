"""
Test checks for installed modules we might use
"""

# Standard Library
from unittest.mock import patch

# AA SRP
from aasrp.app_settings import (
    aa_discordnotify_installed,
    allianceauth_discordbot_installed,
    discordproxy_installed,
)
from aasrp.tests import BaseTestCase


class TestAllianceauthDiscordbotInstalled(BaseTestCase):
    """
    Test allianceauth_discordbot_installed function
    """

    def test_returns_true_when_aadiscordbot_is_installed(self):
        """
        Test returns true when aadiscordbot is installed

        :return:
        :rtype:
        """

        with patch(
            "django.apps.apps.is_installed", return_value=True
        ) as mock_is_installed:

            self.assertTrue(allianceauth_discordbot_installed())
            mock_is_installed.assert_called_once_with(app_name="aadiscordbot")

    def test_returns_false_when_aadiscordbot_is_not_installed(self):
        """
        Test returns false when aadiscordbot is not installed

        :return:
        :rtype:
        """

        with patch(
            "django.apps.apps.is_installed", return_value=False
        ) as mock_is_installed:
            self.assertFalse(allianceauth_discordbot_installed())
            mock_is_installed.assert_called_once_with(app_name="aadiscordbot")


class TestDiscordnotifyInstalled(BaseTestCase):
    """
    Test aa_discordnotify_installed function
    """

    def test_returns_true_when_discordnotify_is_installed(self):
        """
        Test returns true when discordnotify is installed

        :return:
        :rtype:
        """

        with patch(
            "django.apps.apps.is_installed", return_value=True
        ) as mock_is_installed:

            self.assertTrue(aa_discordnotify_installed())
            mock_is_installed.assert_called_once_with(app_name="discordnotify")

    def test_returns_false_when_discordnotify_is_not_installed(self):
        """
        Test returns false when discordnotify is not installed

        :return:
        :rtype:
        """

        with patch(
            "django.apps.apps.is_installed", return_value=False
        ) as mock_is_installed:
            self.assertFalse(aa_discordnotify_installed())
            mock_is_installed.assert_called_once_with(app_name="discordnotify")


class TestDiscordProxyInstalled(BaseTestCase):
    """
    Test discordproxy_installed function
    """

    @patch("discordproxy.client.DiscordClient")
    def test_returns_true_when_discordclient_imported_successfully(
        self, mock_discord_client
    ):
        """
        Test returns true when discordclient import successfully

        :param mock_discord_client:
        :type mock_discord_client:
        :return:
        :rtype:
        """

        result = discordproxy_installed()
        self.assertTrue(result)

    @patch("builtins.__import__", side_effect=ModuleNotFoundError)
    def test_returns_false_when_discordclient_import_fails(self, mock_import):
        """
        Test returns false when discordclient import fails

        :param mock_import:
        :type mock_import:
        :return:
        :rtype:
        """

        result = discordproxy_installed()
        self.assertFalse(result)
