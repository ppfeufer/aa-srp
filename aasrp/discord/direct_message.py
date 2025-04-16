"""
Handling Discord direct messages to a user
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
    Try to send a PM to a user on Discord via allianceauth-discordbot

    :param user_id:
    :type user_id:
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
            msg="allianceauth-discordbot is active, trying to send private message"
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
            send_message(user_id=user_id, embed=embed)
        else:
            send_message(user_id=user_id, message=f"**{title}**\n\n{message}")
    else:
        logger.debug(
            msg=(
                "allianceauth-discordbot is not available on this "
                "system to send the private message"
            )
        )


def _discordproxy_send_private_message(
    user_id: int,
    title: str,
    message: str,
    embed_message: bool = True,
    level: str = "info",
):
    """
    Try to send a PM to a user on Discord via discordproxy
    (fall back to allianceauth-discordbot if needed)

    :param user_id:
    :type user_id:
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
        logger.debug(msg="Trying to send a direct message via discordproxy")

        if embed_message is True:
            # Third Party
            from discordproxy.discord_api_pb2 import Embed

            footer = Embed.Footer(text=str(__title__))
            embed = Embed(
                title=str(title),
                description=message,
                color=DISCORD_EMBED_COLOR_MAP.get(level),
                timestamp=timezone.now().isoformat(),
                footer=footer,
            )

            client.create_direct_message(user_id=user_id, embed=embed)
        else:
            client.create_direct_message(
                user_id=user_id, content=f"**{title}**\n\n{message}"
            )
    except DiscordProxyException as ex:
        # Something went wrong with discordproxy
        # Fail silently and try if allianceauth-discordbot is available
        # as a last ditch effort to get the message out to Discord
        logger.debug(
            msg=(
                "Something went wrong with discordproxy, "
                "cannot send a direct message, trying allianceauth-discordbot "
                f"to send the message if available. Error: {ex}"
            )
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
    Send notification to user
    This creates a notification in Auth and a PM in Discord when either
    Discordproxy, AA-Discordbot or AA Discord Notifications is installed

    :param user:
    :type user:
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

    if message["allianceauth"]:
        getattr(notify, level)(user=user, title=title, message=message["allianceauth"])

    # Handle Discord PMs when aa_discordnotify is not active
    # Check if either allianceauth_discordbot or discordproxy are available
    # to send the PM
    if hasattr(user, "discord"):  # Check if the user has a Discord account
        logger.debug(msg="User has a Discord account")

        # Check if discordnotify is active
        if not aa_discordnotify_installed():
            if discordproxy_installed():
                logger.debug(msg="discordproxy seems to be available ...")

                _discordproxy_send_private_message(
                    user_id=int(user.discord.uid),
                    level=level,
                    title=title,
                    message=message["discord"],
                    embed_message=embed_message,
                )
            else:
                # discordproxy not available, try if allianceauth-discordbot is
                # available
                logger.debug(
                    msg=(
                        "discordproxy not available to send a direct message, "
                        "let's see if we can use allianceauth-discordbot if available"
                    )
                )

                _aadiscordbot_send_private_message(
                    user_id=int(user.discord.uid),
                    level=level,
                    title=title,
                    message=message["discord"],
                    embed_message=embed_message,
                )
        else:
            logger.debug(
                msg="discordnotify is active, we don't have to send the PM ourself."
            )
    else:
        logger.debug(
            msg="User doesn't have a Discord account, can't send any messages ..."
        )
