"""
Handling Discord channel messages
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
    Try to send a message to a channel on Discord via allianceauth-discordbot

    :param channel_id:
    :type channel_id:
    :param title:
    :type title:
    :param message:
    :type message:
    :param embed_message:
    :type embed_message:
    :param level:
    :type level:
    :return:
    :rtype:
    """

    if allianceauth_discordbot_installed():
        logger.debug(
            msg="allianceauth-discordbot is active, trying to send channel message"
        )

        # Third Party
        from aadiscordbot.tasks import send_message
        from discord import Embed

        embed = Embed(
            title=str(title),
            description=message,
            color=DISCORD_EMBED_COLOR_MAP.get(level),
            timestamp=datetime.now(),
        )

        if embed_message is True:
            send_message(channel_id=channel_id, embed=embed)
        else:
            send_message(channel_id=channel_id, message=f"**{title}**\n\n{message}")
    else:
        logger.debug(
            msg=(
                "allianceauth-discordbot is not available on this "
                "system to send the channel message"
            )
        )


def _discordproxy_send_channel_message(
    channel_id: int,
    title: str,
    message: str,
    embed_message: bool = True,
    level: str = "info",
):
    """
    Try to send a message to a channel on Discord via discordproxy
    (fall back to allianceauth-discordbot if needed)

    :param channel_id:
    :type channel_id:
    :param title:
    :type title:
    :param message:
    :type message:
    :param embed_message:
    :type embed_message:
    :param level:
    :type level:
    :return:
    :rtype:
    """

    # Third Party
    from discordproxy.client import DiscordClient
    from discordproxy.exceptions import DiscordProxyException

    target = f"{DISCORDPROXY_HOST}:{DISCORDPROXY_PORT}"
    client = DiscordClient(target=target, timeout=DISCORDPROXY_TIMEOUT)

    try:
        logger.debug(msg="Trying to send a channel message via discordproxy")

        if embed_message:
            # Third Party
            from discordproxy.discord_api_pb2 import Embed

            footer = Embed.Footer(text=str(__title__))

            embed = Embed(
                title=title,
                description=message,
                color=DISCORD_EMBED_COLOR_MAP.get(level),
                timestamp=timezone.now().isoformat(),
                footer=footer,
            )
            client.create_channel_message(channel_id=channel_id, embed=embed)
        else:
            client.create_channel_message(
                channel_id=channel_id, content=f"**{title}**\n\n{message}"
            )
    except DiscordProxyException as ex:
        # Something went wrong with discordproxy
        # Fail silently and try if allianceauth-discordbot is available
        # as a last ditch effort to get the message out to Discord
        logger.debug(
            msg=(
                "Something went wrong with discordproxy, "
                "cannot send a channel message, "
                f"trying allianceauth-discordbot to send the message. Error: {ex}"
            )
        )

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
    Sending a message to a discord channel.
    This creates a message to the SRP Team channel on Discord when either
    Discordproxy or AA-Discordbot is installed

    :param channel_id:
    :type channel_id:
    :param title:
    :type title:
    :param message:
    :type message:
    :param embed_message:
    :type embed_message:
    :return:
    :rtype:
    """

    # Check if either allianceauth_discordbot or discordproxy are available
    # to send the channel message
    if discordproxy_installed():
        logger.debug(msg="discordproxy seems to be available, check if we can use it")

        _discordproxy_send_channel_message(
            channel_id=channel_id,
            level="info",
            title=title,
            message=message,
            embed_message=embed_message,
        )
    else:
        # discordproxy not available, try if allianceauth-discordbot is available
        logger.debug(
            msg=(
                "discordproxy not available to send the channel message, "
                "let's see if we can use allianceauth-discordbot"
            )
        )

        _aadiscordbot_send_channel_message(
            channel_id=channel_id,
            level="info",
            title=title,
            message=message,
            embed_message=embed_message,
        )
