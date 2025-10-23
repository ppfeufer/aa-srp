"""
Test checks for installed modules we might use
"""

# Standard Library
from unittest.mock import patch

# Django
from django.test import modify_settings

# AA SRP
from aasrp.app_settings import (
    aa_discordnotify_installed,
    allianceauth_discordbot_installed,
    discordproxy_installed,
)
from aasrp.tests import BaseTestCase


class TestModulesInstalled(BaseTestCase):
    """
    Test for installed modules
    """

    @modify_settings(INSTALLED_APPS={"remove": "aadiscordbot"})
    def test_allianceauth_discordbot_installed_should_return_false(self):
        """
        Test allianceauth_discordbot_installed should return False

        :return:
        :rtype:
        """

        self.assertFalse(expr=allianceauth_discordbot_installed())

    @modify_settings(INSTALLED_APPS={"append": "aadiscordbot"})
    def test_allianceauth_discordbot_installed_should_return_true(self):
        """
        Test allianceauth_discordbot_installed should return True

        :return:
        :rtype:
        """

        self.assertTrue(expr=allianceauth_discordbot_installed())

    @modify_settings(INSTALLED_APPS={"remove": "discordnotify"})
    def test_aa_discordnotify_installed_should_return_false(self):
        """
        Test aa_discordnotify_installed should return False

        :return:
        :rtype:
        """

        self.assertFalse(expr=aa_discordnotify_installed())

    @modify_settings(INSTALLED_APPS={"append": "discordnotify"})
    def test_aa_discordnotify_installed_should_return_true(self):
        """
        Test aa_discordnotify_installed should return True

        :return:
        :rtype:
        """

        self.assertTrue(expr=aa_discordnotify_installed())

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
