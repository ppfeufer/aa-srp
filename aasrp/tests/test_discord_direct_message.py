"""
Tests for the Discord direct message functionality
."""

# Standard Library
from datetime import datetime
from unittest.mock import MagicMock, patch

# Third Party
from discord import Embed
from discordproxy.exceptions import DiscordProxyException

# AA SRP
from aasrp import __title__
from aasrp.constants import DISCORD_EMBED_COLOR_MAP
from aasrp.discord.direct_message import (
    _aadiscordbot_send_private_message,
    _discordproxy_send_private_message,
    send_user_notification,
)
from aasrp.tests import BaseTestCase


class TestAADiscordbotSendPrivateMessage(BaseTestCase):
    """
    Test suite for the _aadiscordbot_send_private_message function.
    """

    @patch("aadiscordbot.tasks.send_message")
    @patch(
        "aasrp.discord.direct_message.allianceauth_discordbot_installed",
        return_value=True,
    )
    def test_sends_embed_message_when_discordbot_installed(
        self, mock_installed, mock_send_message
    ):
        """
        Test that an embed message is sent when allianceauth-discordbot is installed.

        :param mock_installed:
        :type mock_installed:
        :param mock_send_message:
        :type mock_send_message:
        :return:
        :rtype:
        """

        user_id = 12345
        title = "Test Title"
        message = "Test Message"
        embed_message = True
        level = "info"
        fixed_now = datetime(2025, 9, 22, 14, 26, 46, 452809)

        with (
            patch("discord.Embed", wraps=Embed) as mock_embed,
            patch("aasrp.discord.direct_message.datetime") as mock_datetime,
        ):
            mock_datetime.now.return_value = fixed_now
            _aadiscordbot_send_private_message(
                user_id, title, message, embed_message, level
            )
            mock_embed.assert_called_once_with(
                title=title,
                description=message,
                color=DISCORD_EMBED_COLOR_MAP.get(level),
                timestamp=fixed_now,
            )
            mock_send_message.assert_called_once()

    @patch("aadiscordbot.tasks.send_message")
    @patch(
        "aasrp.discord.direct_message.allianceauth_discordbot_installed",
        return_value=True,
    )
    def test_sends_plain_message_when_embed_message_is_false(
        self, mock_installed, mock_send_message
    ):
        """
        Test that a plain text message is sent when embed_message is False.

        :param mock_installed:
        :type mock_installed:
        :param mock_send_message:
        :type mock_send_message:
        :return:
        :rtype:
        """

        user_id = 12345
        title = "Test Title"
        message = "Test Message"
        embed_message = False
        level = "info"

        _aadiscordbot_send_private_message(
            user_id, title, message, embed_message, level
        )
        mock_send_message.assert_called_once_with(
            user_id=user_id,
            embed=f"**{title}**\n\n{message}",
        )

    @patch("aadiscordbot.tasks.send_message")
    @patch(
        "aasrp.discord.direct_message.allianceauth_discordbot_installed",
        return_value=False,
    )
    def test_logs_message_when_discordbot_not_installed(
        self, mock_installed, mock_send_message
    ):
        """
        Test that a message is logged when allianceauth-discordbot is not installed.

        :param mock_installed:
        :type mock_installed:
        :param mock_send_message:
        :type mock_send_message:
        :return:
        :rtype:
        """

        user_id = 12345
        title = "Test Title"
        message = "Test Message"
        embed_message = True
        level = "info"

        with patch("aasrp.discord.direct_message.logger.debug") as mock_logger:
            _aadiscordbot_send_private_message(
                user_id, title, message, embed_message, level
            )
            mock_logger.assert_called_once_with(
                "allianceauth-discordbot is not available to send the private message"
            )
            mock_send_message.assert_not_called()


class TestDiscordproxySendPrivateMessage(BaseTestCase):
    """
    Test suite for the _discordproxy_send_private_message function.
    """

    @patch("aasrp.discord.direct_message._discordproxy_send_private_message")
    @patch("discordproxy.client.DiscordClient")
    def test_sends_embed_message_via_discordproxy(
        self, mock_discord_client, mock_discordproxy
    ):
        """
        Test that an embed message is sent via discordproxy.

        :param mock_discord_client:
        :type mock_discord_client:
        :param mock_discordproxy:
        :type mock_discordproxy:
        :return:
        :rtype:
        """

        mock_client_instance = MagicMock()
        mock_discord_client.return_value = mock_client_instance
        user_id = 12345
        title = "Test Title"
        message = "Test Message"
        embed_message = True
        level = "info"
        fixed_now = datetime(2025, 9, 22, 14, 43, 53, 423474)

        with (
            patch("django.utils.timezone.now", return_value=fixed_now),
            patch("discordproxy.discord_api_pb2.Embed") as mock_embed,
        ):
            mock_embed_instance = MagicMock()
            mock_embed.return_value = mock_embed_instance
            _discordproxy_send_private_message(
                user_id=user_id,
                title=title,
                message=message,
                embed_message=embed_message,
                level=level,
            )
            mock_embed.assert_called_once_with(
                title=title,
                description=message,
                color=DISCORD_EMBED_COLOR_MAP.get(level),
                timestamp=fixed_now.isoformat(),
                footer=mock_embed.Footer(text=__title__),
            )
            mock_client_instance.create_direct_message.assert_called_once_with(
                user_id=user_id, embed=mock_embed_instance
            )
            mock_discordproxy.assert_not_called()

    @patch("aasrp.discord.direct_message._discordproxy_send_private_message")
    @patch("discordproxy.client.DiscordClient")
    def test_sends_plain_message_via_discordproxy(
        self, mock_discord_client, mock_discordproxy
    ):
        """
        Test that a plain text message is sent via discordproxy.

        :param mock_discord_client:
        :type mock_discord_client:
        :param mock_discordproxy:
        :type mock_discordproxy:
        :return:
        :rtype:
        """

        mock_client_instance = MagicMock()
        mock_discord_client.return_value = mock_client_instance
        user_id = 12345
        title = "Test Title"
        message = "Test Message"
        embed_message = False
        level = "info"

        _discordproxy_send_private_message(
            user_id=user_id,
            title=title,
            message=message,
            embed_message=embed_message,
            level=level,
        )
        mock_client_instance.create_direct_message.assert_called_once_with(
            user_id=user_id, content=f"**{title}**\n\n{message}"
        )
        mock_discordproxy.assert_not_called()

    @patch("aasrp.discord.direct_message._aadiscordbot_send_private_message")
    @patch("discordproxy.client.DiscordClient")
    def test_falls_back_to_aadiscordbot_when_discordproxy_fails(
        self, mock_discord_client, mock_fallback
    ):
        mock_client_instance = MagicMock()
        mock_discord_client.return_value = mock_client_instance
        mock_client_instance.create_direct_message.side_effect = DiscordProxyException(
            "Error"
        )
        user_id = 12345
        title = "Test Title"
        message = "Test Message"
        embed_message = True
        level = "info"

        _discordproxy_send_private_message(
            user_id=user_id,
            title=title,
            message=message,
            embed_message=embed_message,
            level=level,
        )
        mock_fallback.assert_called_once_with(
            user_id=user_id,
            title=title,
            message=message,
            embed_message=embed_message,
            level=level,
        )


class TestSendUserNotification(BaseTestCase):
    """
    Test suite for the send_user_notification function.
    """

    @patch(
        "aasrp.discord.direct_message.aa_discordnotify_installed", return_value=False
    )
    @patch("aasrp.discord.direct_message.discordproxy_installed", return_value=True)
    @patch("aasrp.discord.direct_message._discordproxy_send_private_message")
    @patch("aasrp.discord.direct_message._aadiscordbot_send_private_message")
    @patch("aasrp.discord.direct_message.notify")
    def test_sends_notification_with_discord_discordproxy(
        self,
        mock_notify,
        mock_aadiscordbot,
        mock_discordproxy,
        mock_discordproxy_installed,
        mock_aa_discordnotify_installed,
    ):
        """
        Test that a notification is sent using discordproxy when available.

        :param mock_notify:
        :type mock_notify:
        :param mock_aadiscordbot:
        :type mock_aadiscordbot:
        :param mock_discordproxy:
        :type mock_discordproxy:
        :param mock_discordproxy_installed:
        :type mock_discordproxy_installed:
        :param mock_aa_discordnotify_installed:
        :type mock_aa_discordnotify_installed:
        :return:
        :rtype:
        """

        user = MagicMock()
        user.discord.uid = "12345"
        message = {"allianceauth": "Auth message", "discord": "Discord message"}
        title = "Notification Title"
        level = "info"

        send_user_notification(user, title, message, embed_message=True, level=level)

        mock_notify.info.assert_called_once_with(
            user=user, title=title, message=message["allianceauth"]
        )
        mock_discordproxy.assert_called_once_with(
            user_id=12345,
            title=title,
            message=message["discord"],
            embed_message=True,
            level=level,
        )
        mock_aadiscordbot.assert_not_called()

    @patch("aasrp.discord.direct_message._aadiscordbot_send_private_message")
    @patch(
        "aasrp.discord.direct_message.aa_discordnotify_installed", return_value=False
    )
    @patch("aasrp.discord.direct_message.discordproxy_installed", return_value=False)
    @patch("aasrp.discord.direct_message.notify")
    def test_falls_back_to_aadiscordbot_when_discordproxy_unavailable(
        self,
        mock_notify,
        mock_discordproxy_installed,
        mock_aa_discordnotify_installed,
        mock_aadiscordbot,
    ):
        """
        Test that a notification falls back to allianceauth-discordbot when discordproxy is unavailable.

        :param mock_notify:
        :type mock_notify:
        :param mock_discordproxy_installed:
        :type mock_discordproxy_installed:
        :param mock_aa_discordnotify_installed:
        :type mock_aa_discordnotify_installed:
        :param mock_aadiscordbot:
        :type mock_aadiscordbot:
        :return:
        :rtype:
        """

        user = MagicMock()
        user.discord.uid = "12345"
        message = {"allianceauth": "Auth message", "discord": "Discord message"}
        title = "Notification Title"
        level = "info"

        send_user_notification(user, title, message, embed_message=True, level=level)

        mock_notify.info.assert_called_once_with(
            user=user, title=title, message=message["allianceauth"]
        )
        mock_aadiscordbot.assert_called_once_with(
            user_id=12345,
            title=title,
            message=message["discord"],
            embed_message=True,
            level=level,
        )

    @patch("aasrp.discord.direct_message.logger.debug")
    @patch("aasrp.discord.direct_message.notify")
    def test_does_not_send_notification_when_user_has_no_discord_account(
        self, mock_notify, mock_logger
    ):
        """
        Test that no Discord notification is sent when the user has no Discord account.

        :param mock_notify:
        :type mock_notify:
        :param mock_logger:
        :type mock_logger:
        :return:
        :rtype:
        """

        user = MagicMock()
        del user.discord
        message = {"allianceauth": "Auth message", "discord": "Discord message"}
        title = "Notification Title"
        level = "info"

        send_user_notification(user, title, message, embed_message=True, level=level)

        mock_notify.info.assert_called_once_with(
            user=user, title=title, message=message["allianceauth"]
        )
        mock_logger.assert_called_with(
            "User doesn't have a Discord account, can't send any messages ..."
        )

    @patch("aasrp.discord.direct_message.aa_discordnotify_installed", return_value=True)
    @patch("aasrp.discord.direct_message.logger.debug")
    @patch("aasrp.discord.direct_message.notify")
    def test_skips_sending_pm_when_discordnotify_is_active(
        self, mock_notify, mock_logger, mock_aa_discordnotify_installed
    ):
        """
        Test that no Discord notification is sent when AA Discord Notifications is active.

        :param mock_notify:
        :type mock_notify:
        :param mock_logger:
        :type mock_logger:
        :param mock_aa_discordnotify_installed:
        :type mock_aa_discordnotify_installed:
        :return:
        :rtype:
        """

        user = MagicMock()
        user.discord.uid = "12345"
        message = {"allianceauth": "Auth message", "discord": "Discord message"}
        title = "Notification Title"
        level = "info"

        send_user_notification(user, title, message, embed_message=True, level=level)

        mock_notify.info.assert_called_once_with(
            user=user, title=title, message=message["allianceauth"]
        )
        mock_logger.assert_called_with(
            "discordnotify is active, no need to send the DM ourselves."
        )

    @patch("aasrp.discord.direct_message.notify")
    def test_sends_allianceauth_notification_when_message_provided(self, mock_notify):
        user = MagicMock()
        message = {"allianceauth": "Auth message", "discord": "Discord message"}
        title = "Notification Title"
        level = "info"

        send_user_notification(user, title, message, embed_message=True, level=level)

        mock_notify.info.assert_called_once_with(
            user=user, title=title, message=message["allianceauth"]
        )

    @patch("aasrp.discord.direct_message.notify")
    def test_does_not_send_allianceauth_notification_when_message_missing(
        self, mock_notify
    ):
        user = MagicMock()
        message = {"allianceauth": "", "discord": "Discord message"}
        title = "Notification Title"
        level = "info"

        send_user_notification(user, title, message, embed_message=True, level=level)

        mock_notify.info.assert_not_called()
