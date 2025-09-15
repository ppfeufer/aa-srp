"""
Handling Discord channel messages

This module provides functionality to send messages to Discord channels.
It supports two methods for sending messages:
1. `discordproxy`: A proxy service for interacting with Discord.
2. `allianceauth-discordbot`: A bot integrated with Alliance Auth.

The module determines the availability of these methods and uses the appropriate one
to send messages. If `discordproxy` is unavailable, it falls back to `allianceauth-discordbot`.

Functions:
- `_aadiscordbot_send_channel_message`: Sends a message to a Discord channel using `allianceauth-discordbot`.
- `_discordproxy_send_channel_message`: Sends a message to a Discord channel using `discordproxy`, with a fallback to `allianceauth-discordbot`.
- `send_message_to_discord_channel`: High-level function to send a message to a Discord channel, selecting the appropriate method based on availability.
"""

# pylint: disable=import-outside-toplevel, duplicate-code

# Standard Library
from datetime import datetime

# Django
from django.utils import timezone

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__
from aasrp.app_settings import (
    DISCORDPROXY_HOST,
    DISCORDPROXY_PORT,
    DISCORDPROXY_TIMEOUT,
    allianceauth_discordbot_installed,
    discordproxy_installed,
)
from aasrp.constants import DISCORD_EMBED_COLOR_MAP

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def _aadiscordbot_send_channel_message(
    channel_id: int,
    title: str,
    message: str,
    embed_message: bool = True,
    level: str = "info",
) -> None:
    """
    Try to send a message to a channel on Discord via allianceauth-discordbot.

    This function attempts to send a message to a specified Discord channel using
    the `allianceauth-discordbot` integration. If the bot is not installed, it logs
    a debug message indicating the unavailability.

    :param channel_id: The ID of the Discord channel where the message will be sent.
    :type channel_id: int
    :param title: The title of the message.
    :type title: str
    :param message: The content of the message.
    :type message: str
    :param embed_message: Whether to send the message as an embed (default: True).
    :type embed_message: bool
    :param level: The severity level of the message (e.g., "info", "warning"). Default is "info".
    :type level: str
    :return: None
    :rtype: None
    """

    # Check if allianceauth-discordbot is installed
    if allianceauth_discordbot_installed():
        logger.debug(
            "allianceauth-discordbot is active, trying to send channel message"
        )

        # Import the send_message task and Embed class
        # Third Party
        from aadiscordbot.tasks import send_message
        from discord import Embed

        # Create an embed object with the provided details
        embed = Embed(
            title=title,
            description=message,
            color=DISCORD_EMBED_COLOR_MAP.get(level),
            timestamp=datetime.now(),
        )

        # Send the message to the specified channel
        send_message(
            channel_id=channel_id,
            embed=embed if embed_message else f"**{title}**\n\n{message}",
        )
    else:
        # Log a debug message if the bot is not available
        logger.debug(
            "allianceauth-discordbot is not available on this system to send the channel message"
        )


def _discordproxy_send_channel_message(
    channel_id: int,
    title: str,
    message: str,
    embed_message: bool = True,
    level: str = "info",
):
    """
    Try to send a message to a channel on Discord via discordproxy.

    This function attempts to send a message to a specified Discord channel using
    the `discordproxy` service. If the message cannot be sent due to an exception,
    it falls back to using the `allianceauth-discordbot` method.

    :param channel_id: The ID of the Discord channel where the message will be sent.
    :type channel_id: int
    :param title: The title of the message.
    :type title: str
    :param message: The content of the message.
    :type message: str
    :param embed_message: Whether to send the message as an embed (default: True).
    :type embed_message: bool
    :param level: The severity level of the message (e.g., "info", "warning"). Default is "info".
    :type level: str
    :return: None
    :rtype: None
    """

    # Import the necessary classes and exceptions from the discordproxy library
    # Third Party
    from discordproxy.client import DiscordClient
    from discordproxy.exceptions import DiscordProxyException

    # Define the target address for the Discord proxy service
    target = f"{DISCORDPROXY_HOST}:{DISCORDPROXY_PORT}"
    client = DiscordClient(target=target, timeout=DISCORDPROXY_TIMEOUT)

    try:
        # Log the attempt to send a message via discordproxy
        logger.debug("Trying to send a channel message via discordproxy")

        if embed_message:
            # Import the Embed class for creating embed messages
            # Third Party
            from discordproxy.discord_api_pb2 import Embed

            # Create an embed object with the provided details
            embed = Embed(
                title=title,
                description=message,
                color=DISCORD_EMBED_COLOR_MAP.get(level),
                timestamp=timezone.now().isoformat(),
                footer=Embed.Footer(text=str(__title__)),
            )
            # Send the embed message to the specified channel
            client.create_channel_message(channel_id=channel_id, embed=embed)
        else:
            # Send a plain text message to the specified channel
            client.create_channel_message(
                channel_id=channel_id, content=f"**{title}**\n\n{message}"
            )
    except DiscordProxyException as ex:
        # Log the exception and fall back to allianceauth-discordbot
        logger.debug(
            "Something went wrong with discordproxy, cannot send a channel message. "
            f"Trying allianceauth-discordbot. Error: {ex}"
        )
        # Use the allianceauth-discordbot method as a fallback
        _aadiscordbot_send_channel_message(
            channel_id=channel_id,
            level=level,
            title=title,
            message=message,
            embed_message=True,
        )


def send_message_to_discord_channel(
    channel_id: int, title: str, message: str, embed_message: bool = True
) -> None:
    """
    Send a message to a Discord channel.

    This function sends a message to a specified Discord channel. It first checks
    if `discordproxy` is available and uses it to send the message. If `discordproxy`
    is not available, it falls back to using `allianceauth-discordbot`.

    :param channel_id: The ID of the Discord channel where the message will be sent.
    :type channel_id: int
    :param title: The title of the message.
    :type title: str
    :param message: The content of the message.
    :type message: str
    :param embed_message: Whether to send the message as an embed (default: True).
    :type embed_message: bool
    :return: None
    :rtype: None
    """

    # Check if either allianceauth_discordbot or discordproxy are available
    # to send the channel message
    if discordproxy_installed():
        logger.debug("discordproxy is available, attempting to use it")

        # Use discordproxy to send the message
        _discordproxy_send_channel_message(
            channel_id=channel_id,
            level="info",
            title=title,
            message=message,
            embed_message=embed_message,
        )
    else:
        logger.debug(
            "discordproxy not available, falling back to allianceauth-discordbot"
        )

        # Use allianceauth-discordbot to send the message
        _aadiscordbot_send_channel_message(
            channel_id=channel_id,
            level="info",
            title=title,
            message=message,
            embed_message=embed_message,
        )
