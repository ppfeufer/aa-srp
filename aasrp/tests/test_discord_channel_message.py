# Standard Library
from unittest.mock import ANY, MagicMock, patch

# Third Party
from discordproxy.exceptions import DiscordProxyException

# AA SRP
from aasrp.constants import DISCORD_EMBED_COLOR_MAP
from aasrp.discord.channel_message import (
    _aadiscordbot_send_channel_message,
    _discordproxy_send_channel_message,
    send_message_to_discord_channel,
)
from aasrp.tests import BaseTestCase


class TestAadiscordbotSendChannelMessage(BaseTestCase):
    """
    Test cases for the _aadiscordbot_send_channel_message function.
    """

    @patch(
        "aasrp.discord.channel_message.allianceauth_discordbot_installed",
        return_value=True,
    )
    @patch("aadiscordbot.tasks.send_message")
    @patch("discord.Embed")
    def test_sends_embed_message_when_bot_is_installed(
        self, mock_embed, mock_send_message, mock_bot_installed
    ):
        """
        Test that an embed message is sent when the bot is installed.

        :param mock_embed:
        :type mock_embed:
        :param mock_send_message:
        :type mock_send_message:
        :param mock_bot_installed:
        :type mock_bot_installed:
        :return:
        :rtype:
        """

        mock_embed.return_value = MagicMock()
        _aadiscordbot_send_channel_message(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=True,
            level="info",
        )
        mock_embed.assert_called_once_with(
            title="Test Title",
            description="Test Message",
            color=DISCORD_EMBED_COLOR_MAP.get("info"),
            timestamp=ANY,
        )
        mock_send_message.assert_called_once_with(
            channel_id=12345, embed=mock_embed.return_value
        )

    @patch(
        "aasrp.discord.channel_message.allianceauth_discordbot_installed",
        return_value=True,
    )
    @patch("aadiscordbot.tasks.send_message")
    def test_sends_plain_message_when_embed_is_disabled(
        self, mock_send_message, mock_bot_installed
    ):
        """
        Test that a plain text message is sent when embed_message is False.

        :param mock_send_message:
        :type mock_send_message:
        :param mock_bot_installed:
        :type mock_bot_installed:
        :return:
        :rtype:
        """

        _aadiscordbot_send_channel_message(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=False,
            level="info",
        )
        mock_send_message.assert_called_once_with(
            channel_id=12345, embed="**Test Title**\n\nTest Message"
        )

    @patch(
        "aasrp.discord.channel_message.allianceauth_discordbot_installed",
        return_value=False,
    )
    @patch("aasrp.discord.channel_message.logger")
    def test_logs_debug_message_when_bot_is_not_installed(
        self, mock_logger, mock_bot_installed
    ):
        """
        Test that a debug message is logged when the bot is not installed.

        :param mock_logger:
        :type mock_logger:
        :param mock_bot_installed:
        :type mock_bot_installed:
        :return:
        :rtype:
        """

        _aadiscordbot_send_channel_message(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=True,
            level="info",
        )
        mock_logger.debug.assert_called_once_with(
            "allianceauth-discordbot is not available on this system to send the channel message"
        )


class TestDiscordproxySendChannelMessage(BaseTestCase):
    """
    Test cases for the _discordproxy_send_channel_message function.
    """

    @patch("aasrp.discord.channel_message._aadiscordbot_send_channel_message")
    @patch("discordproxy.client.DiscordClient.create_channel_message")
    @patch("discordproxy.discord_api_pb2.Embed")
    def test_sends_embed_message_via_discordproxy_when_available(
        self, mock_embed, mock_create_channel_message, mock_fallback
    ):
        """
        Test that an embed message is sent via discordproxy when available.

        :param mock_embed:
        :type mock_embed:
        :param mock_create_channel_message:
        :type mock_create_channel_message:
        :param mock_fallback:
        :type mock_fallback:
        :return:
        :rtype:
        """

        mock_embed.return_value = MagicMock()
        _discordproxy_send_channel_message(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=True,
            level="info",
        )
        mock_embed.assert_called_once_with(
            title="Test Title",
            description="Test Message",
            color=DISCORD_EMBED_COLOR_MAP.get("info"),
            timestamp=ANY,
            footer=ANY,
        )
        mock_create_channel_message.assert_called_once_with(
            channel_id=12345, embed=mock_embed.return_value
        )
        mock_fallback.assert_not_called()

    @patch("aasrp.discord.channel_message._aadiscordbot_send_channel_message")
    @patch("discordproxy.client.DiscordClient.create_channel_message")
    def test_sends_plain_message_via_discordproxy_when_embed_is_disabled(
        self, mock_create_channel_message, mock_fallback
    ):
        """
        Test that a plain text message is sent via discordproxy when embed_message is False.

        :param mock_create_channel_message:
        :type mock_create_channel_message:
        :param mock_fallback:
        :type mock_fallback:
        :return:
        :rtype:
        """

        _discordproxy_send_channel_message(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=False,
            level="info",
        )
        mock_create_channel_message.assert_called_once_with(
            channel_id=12345, content="**Test Title**\n\nTest Message"
        )
        mock_fallback.assert_not_called()

    @patch("aasrp.discord.channel_message._aadiscordbot_send_channel_message")
    @patch("discordproxy.client.DiscordClient.create_channel_message")
    @patch("discordproxy.discord_api_pb2.Embed")
    def test_falls_back_to_aadiscordbot_when_discordproxy_raises_exception(
        self, mock_embed, mock_create_channel_message, mock_fallback
    ):
        """
        Test that it falls back to aadiscordbot when discordproxy raises an exception.

        :param mock_embed:
        :type mock_embed:
        :param mock_create_channel_message:
        :type mock_create_channel_message:
        :param mock_fallback:
        :type mock_fallback:
        :return:
        :rtype:
        """

        mock_create_channel_message.side_effect = DiscordProxyException("Error")
        _discordproxy_send_channel_message(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=True,
            level="info",
        )
        mock_create_channel_message.assert_called_once()
        mock_fallback.assert_called_once_with(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=True,
            level="info",
        )


class TestSendMessageToDiscordChannel(BaseTestCase):
    """
    Test cases for the send_message_to_discord_channel function.
    """

    @patch("aasrp.discord.channel_message._discordproxy_send_channel_message")
    @patch("aasrp.discord.channel_message._aadiscordbot_send_channel_message")
    @patch("aasrp.discord.channel_message.discordproxy_installed", return_value=True)
    def test_uses_discordproxy_when_available(
        self, mock_discordproxy_installed, mock_aadiscordbot, mock_discordproxy
    ):
        """
        Test that discordproxy is used when available.

        :param mock_discordproxy_installed:
        :type mock_discordproxy_installed:
        :param mock_aadiscordbot:
        :type mock_aadiscordbot:
        :param mock_discordproxy:
        :type mock_discordproxy:
        :return:
        :rtype:
        """

        send_message_to_discord_channel(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=True,
        )
        mock_discordproxy.assert_called_once_with(
            channel_id=12345,
            level="info",
            title="Test Title",
            message="Test Message",
            embed_message=True,
        )
        mock_aadiscordbot.assert_not_called()

    @patch("aasrp.discord.channel_message._discordproxy_send_channel_message")
    @patch("aasrp.discord.channel_message._aadiscordbot_send_channel_message")
    @patch("aasrp.discord.channel_message.discordproxy_installed", return_value=False)
    def test_falls_back_to_aadiscordbot_when_discordproxy_not_available(
        self, mock_discordproxy_installed, mock_aadiscordbot, mock_discordproxy
    ):
        """
        Test that it falls back to aadiscordbot when discordproxy is not available.

        :param mock_discordproxy_installed:
        :type mock_discordproxy_installed:
        :param mock_aadiscordbot:
        :type mock_aadiscordbot:
        :param mock_discordproxy:
        :type mock_discordproxy:
        :return:
        :rtype:
        """

        send_message_to_discord_channel(
            channel_id=12345,
            title="Test Title",
            message="Test Message",
            embed_message=False,
        )
        mock_aadiscordbot.assert_called_once_with(
            channel_id=12345,
            level="info",
            title="Test Title",
            message="Test Message",
            embed_message=False,
        )
        mock_discordproxy.assert_not_called()
