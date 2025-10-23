"""
Handling Discord direct messages to a user

This module provides functionality to send direct messages to users on Discord.
It supports multiple methods for sending messages, including `discordproxy` and
`allianceauth-discordbot`, and falls back to available options if one method fails.

The module also integrates with Alliance Auth notifications to ensure users are
notified both within the application and on Discord, if applicable.
"""

# pylint: disable=import-outside-toplevel, duplicate-code

# Standard Library
from datetime import datetime

# Django
from django.contrib.auth.models import User
from django.utils import timezone

# Alliance Auth
from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__
from aasrp.app_settings import (
    DISCORDPROXY_HOST,
    DISCORDPROXY_PORT,
    DISCORDPROXY_TIMEOUT,
    aa_discordnotify_installed,
    allianceauth_discordbot_installed,
    discordproxy_installed,
)
from aasrp.constants import DISCORD_EMBED_COLOR_MAP

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def _aadiscordbot_send_private_message(
    user_id: int,
    title: str,
    message: str,
    embed_message: bool = True,
    level: str = "info",
) -> None:
    """
    Send a private message to a user on Discord using allianceauth-discordbot.

    This function attempts to send a private message to a Discord user via the
    allianceauth-discordbot integration. It supports both embedded and plain text
    messages. If the integration is not available, the function logs the unavailability
    and does not send the message.

    :param user_id: The Discord user ID of the recipient.
    :type user_id: int
    :param title: The title of the message.
    :type title: str
    :param message: The content of the message.
    :type message: str
    :param embed_message: Whether to send the message as an embed (default: True).
    :type embed_message: bool
    :param level: The severity level of the message (e.g., "info", "warning").
    :type level: str
    :return: None
    :rtype: None
    """

    if allianceauth_discordbot_installed():
        logger.debug(
            "allianceauth-discordbot is active, trying to send private message"
        )

        # Third Party
        from aadiscordbot.tasks import send_message
        from discord import Embed

        embed = Embed(
            title=title,
            description=message,
            color=DISCORD_EMBED_COLOR_MAP.get(level),
            timestamp=datetime.now(),
        )

        send_message(
            user_id=user_id,
            embed=embed if embed_message else f"**{title}**\n\n{message}",
        )
    else:
        logger.debug(
            "allianceauth-discordbot is not available to send the private message"
        )


def _discordproxy_send_private_message(
    user_id: int,
    title: str,
    message: str,
    embed_message: bool = True,
    level: str = "info",
):
    """
    Try to send a private message (PM) to a user on Discord via discordproxy.
    If discordproxy fails, it falls back to allianceauth-discordbot.

    :param user_id: The Discord user ID of the recipient.
    :type user_id: int
    :param title: The title of the message.
    :type title: str
    :param message: The content of the message.
    :type message: str
    :param embed_message: Whether to send the message as an embed (default: True).
    :type embed_message: bool
    :param level: The severity level of the message (e.g., "info", "warning").
    :type level: str
    :return: None
    :rtype: None
    """

    # Import the Discord client and exception classes from discordproxy
    # Third Party
    from discordproxy.client import DiscordClient
    from discordproxy.exceptions import DiscordProxyException

    # Define the target address for the discordproxy client
    target = f"{DISCORDPROXY_HOST}:{DISCORDPROXY_PORT}"
    client = DiscordClient(target=target, timeout=DISCORDPROXY_TIMEOUT)

    try:
        # Log the attempt to send a direct message via discordproxy
        logger.debug("Trying to send a direct message via discordproxy")

        if embed_message:
            # Import the Embed class for creating embedded messages
            # Third Party
            from discordproxy.discord_api_pb2 import Embed

            # Create an embedded message with the provided details
            embed = Embed(
                title=title,
                description=message,
                color=DISCORD_EMBED_COLOR_MAP.get(level),
                timestamp=timezone.now().isoformat(),
                footer=Embed.Footer(text=str(__title__)),
            )

            # Send the embedded message to the user
            client.create_direct_message(user_id=user_id, embed=embed)
        else:
            # Send a plain text message to the user
            client.create_direct_message(
                user_id=user_id, content=f"**{title}**\n\n{message}"
            )
    except DiscordProxyException as ex:
        # Log the error and attempt to send the message using allianceauth-discordbot
        logger.debug(
            "Something went wrong with discordproxy, cannot send a direct message. "
            "Trying allianceauth-discordbot if available. Error: %s",
            ex,
        )
        _aadiscordbot_send_private_message(
            user_id=user_id,
            level=level,
            title=title,
            message=message,
            embed_message=embed_message,
        )


def send_user_notification(
    user: User,
    title: str,
    message: dict[str, str],
    embed_message: bool = True,
    level: str = "info",
) -> None:
    """
    Send a notification to a user.

    This function creates a notification in Alliance Auth and sends a private message
    (PM) on Discord if the user has a Discord account. It uses one of the following
    methods for sending Discord messages:
    - `discordproxy`
    - `allianceauth-discordbot`
    - `AA Discord Notifications`

    If `discordproxy` and `allianceauth-discordbot` are unavailable, the function logs
    the failure and does not send the message.

    :param user: The user to whom the notification will be sent.
    :type user: User
    :param title: The title of the notification/message.
    :type title: str
    :param message: A dictionary containing the message content for Alliance Auth and Discord. Keys: "allianceauth", "discord".
    :type message: dict[str, str]
    :param embed_message: Whether to send the Discord message as an embed (default: True).
    :type embed_message: bool
    :param level: The severity level of the notification (e.g., "info", "warning"). Default is "info".
    :type level: str
    :return: None
    :rtype: None
    """

    # Send a notification within Alliance Auth if the "allianceauth" message is provided
    if message["allianceauth"]:
        getattr(notify, level)(user=user, title=title, message=message["allianceauth"])

    # Check if the user has a Discord account
    if hasattr(user, "discord"):
        logger.debug("User has a Discord account")

        # Check if AA Discord Notifications is not installed
        if not aa_discordnotify_installed():
            # Use discordproxy if available
            if discordproxy_installed():
                logger.debug("discordproxy seems to be available ...")
                _discordproxy_send_private_message(
                    user_id=int(user.discord.uid),
                    level=level,
                    title=title,
                    message=message["discord"],
                    embed_message=embed_message,
                )
            else:
                # Fall back to allianceauth-discordbot if discordproxy is unavailable
                logger.debug(
                    "discordproxy not available, trying allianceauth-discordbot if available"
                )
                _aadiscordbot_send_private_message(
                    user_id=int(user.discord.uid),
                    level=level,
                    title=title,
                    message=message["discord"],
                    embed_message=embed_message,
                )
        else:
            # Log that AA Discord Notifications is active
            logger.debug("discordnotify is active, no need to send the DM ourselves.")
    else:
        # Log that the user does not have a Discord account
        logger.debug("User doesn't have a Discord account, can't send any messages ...")
