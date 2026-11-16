"""
Test checks for installed modules we might use
"""

# Standard Library
import importlib
from unittest.mock import patch

# AA SRP
from aasrp.app_settings import (
    aa_discordnotify_installed,
    allianceauth_discordbot_installed,
    discordproxy_installed,
    fittings_installed,
    killboard_settings,
)
from aasrp.tests import BaseTestCase

MODULE_AppSettings = "aasrp.app_settings"
MODULE_DjangoApps = "django.apps"


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
            MODULE_DjangoApps + ".apps.is_installed", return_value=True
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
            MODULE_DjangoApps + ".apps.is_installed", return_value=False
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
            MODULE_DjangoApps + ".apps.is_installed", return_value=True
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
            MODULE_DjangoApps + ".apps.is_installed", return_value=False
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

    @patch("builtins.__import__")
    def test_returns_false_when_discordclient_import_fails(self, mock_import):
        """
        Test returns false when discordclient import fails

        :param mock_import:
        :type mock_import:
        :return:
        :rtype:
        """

        # Make the mocked __import__ raise ModuleNotFoundError only for
        # imports that target the discordproxy package. This avoids breaking
        # unrelated imports (coverage, test infrastructure) while still
        # simulating that discordproxy cannot be imported.
        # Capture the original import implementation from importlib so we
        # don't end up calling the mocked `__import__` and recursing.
        real_import = importlib.__import__

        def selective_import(name, globals=None, locals=None, fromlist=(), level=0):
            if isinstance(name, str) and name.startswith("discordproxy"):
                raise ModuleNotFoundError
            return real_import(name, globals, locals, fromlist, level)

        mock_import.side_effect = selective_import

        result = discordproxy_installed()

        self.assertFalse(result)


class TestKillboardSettings(BaseTestCase):
    """
    Test killboard_settings function
    """

    def test_returns_expected_fields_for_known_killboard(self):
        """
        Test that the function returns the expected fields for a known killboard.

        :return:
        """

        with patch(
            MODULE_AppSettings + ".KILLBOARD_DATA",
            {
                "KnownBoard": {
                    "base_url": "https://example.invalid/",
                    "base_url_regex": r"^https://example\\.invalid/",
                    "killmail_url_regex": r"^https://example\\.invalid/kill/\\d+/$",
                    "ignored": "value",
                }
            },
        ):
            result = killboard_settings("KnownBoard")

        self.assertEqual(
            result,
            {
                "base_url": "https://example.invalid/",
                "base_url_regex": r"^https://example\\.invalid/",
                "killmail_url_regex": r"^https://example\\.invalid/kill/\\d+/$",
            },
        )

    def test_includes_api_url_when_present(self):
        """
        Test that the function includes the api_url when it is present in the killboard data.

        :return:
        """

        source = {
            "base_url": "https://example.invalid/",
            "api_url": "https://example.invalid/api/",
            "base_url_regex": "base pattern",
            "killmail_url_regex": "killmail pattern",
            "ignored": "value",
        }

        with patch(MODULE_AppSettings + ".KILLBOARD_DATA", {"KnownBoard": source}):
            self.assertEqual(
                killboard_settings("KnownBoard"),
                {key: value for key, value in source.items() if key != "ignored"},
            )

    def test_raises_keyerror_for_unknown_killboard_name(self):
        """
        Test that the function raises a KeyError when an unknown killboard name is provided.

        :return:
        """

        with patch(MODULE_AppSettings + ".KILLBOARD_DATA", {}):
            with self.assertRaises(KeyError):
                killboard_settings("MissingBoard")

    def test_raises_keyerror_when_required_setting_key_is_missing(self):
        """
        Test that the function raises a KeyError when a required setting key is missing in the killboard data.

        :return:
        """

        with patch(
            MODULE_AppSettings + ".KILLBOARD_DATA",
            {
                "KnownBoard": {
                    "base_url": "https://example.invalid/",
                    "base_url_regex": r"^https://example\\.invalid/",
                }
            },
        ):
            with self.assertRaises(KeyError):
                killboard_settings("KnownBoard")


class TestFittingsInstalled(BaseTestCase):
    """
    Test fittings_installed function
    """

    def test_returns_true_when_fittings_is_installed(self):
        """
        Test returns true when fittings is installed

        :return:
        :rtype:
        """

        with patch(
            MODULE_DjangoApps + ".apps.is_installed", return_value=True
        ) as mock_is_installed:
            self.assertTrue(fittings_installed())
            mock_is_installed.assert_called_once_with(app_name="fittings")

    def test_returns_false_when_fittings_is_not_installed(self):
        """
        Test returns false when fittings is not installed

        :return:
        :rtype:
        """

        with patch(
            MODULE_DjangoApps + ".apps.is_installed", return_value=False
        ) as mock_is_installed:
            self.assertFalse(fittings_installed())
            mock_is_installed.assert_called_once_with(app_name="fittings")
