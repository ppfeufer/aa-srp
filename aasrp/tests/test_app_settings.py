"""
Test checks for installed modules we might use
"""

# Django
from django.test import TestCase, modify_settings, override_settings

# AA SRP
from aasrp.app_settings import (
    aa_discordnotify_installed,
    allianceauth_discordbot_installed,
    debug_enabled,
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


class TestDebugCheck(TestCase):
    """
    Test if debug is enabled
    """

    @override_settings(DEBUG=True)
    def test_debug_enabled_with_debug_true(self) -> None:
        """
        Test debug_enabled with DEBUG = True

        :return:
        :rtype:
        """

        self.assertTrue(debug_enabled())

    @override_settings(DEBUG=False)
    def test_debug_enabled_with_debug_false(self) -> None:
        """
        Test debug_enabled with DEBUG = False

        :return:
        :rtype:
        """

        self.assertFalse(debug_enabled())
