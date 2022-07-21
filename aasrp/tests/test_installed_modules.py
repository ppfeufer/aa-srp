"""
Test checks for installed modules we might use
"""

# Django
from django.test import TestCase, modify_settings

# AA SRP
from aasrp.app_settings import (
    aa_discordnotify_installed,
    allianceauth_discordbot_installed,
)


class TestModulesInstalled(TestCase):
    """
    Test for installed modules
    """

    @modify_settings(INSTALLED_APPS={"remove": "aadiscordbot"})
    def test_allianceauth_discordbot_installed_should_return_false(self):
        """
        Test allianceauth_discordbot_installed should return False
        :return:
        """

        self.assertFalse(allianceauth_discordbot_installed())

    @modify_settings(INSTALLED_APPS={"append": "aadiscordbot"})
    def test_allianceauth_discordbot_installed_should_return_true(self):
        """
        Test allianceauth_discordbot_installed should return True
        :return:
        """

        self.assertTrue(allianceauth_discordbot_installed())

    @modify_settings(INSTALLED_APPS={"remove": "discordnotify"})
    def test_aa_discordnotify_installed_should_return_false(self):
        """
        Test aa_discordnotify_installed should return False
        :return:
        """

        self.assertFalse(aa_discordnotify_installed())

    @modify_settings(INSTALLED_APPS={"append": "discordnotify"})
    def test_aa_discordnotify_installed_should_return_true(self):
        """
        Test aa_discordnotify_installed should return True
        :return:
        """

        self.assertTrue(aa_discordnotify_installed())
