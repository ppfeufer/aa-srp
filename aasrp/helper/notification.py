"""
Notifications helper
"""

# pylint: disable=import-outside-toplevel

# Standard Library
from datetime import datetime

# Django
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Alliance Auth
from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import site_absolute_url

# AA SRP
from aasrp import __title__
from aasrp.app_settings import (
    aa_discordnotify_installed,
    allianceauth_discordbot_installed,
    discordproxy_installed,
)
from aasrp.constants import DISCORD_EMBED_COLOR_MAP
from aasrp.models import Setting, SrpRequest

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
            "allianceauth-discordbot is active, trying to send private message"
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
            "allianceauth-discordbot is not available on this "
            "system to send the private message"
        )


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
            "allianceauth-discordbot is active, trying to send channel message"
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
            "allianceauth-discordbot is not available on this "
            "system to send the channel message"
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

    client = DiscordClient()

    try:
        logger.debug("Trying to send a direct message via discordproxy")

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
            "Something went wrong with discordproxy, "
            "cannot send a direct message, trying allianceauth-discordbot "
            f"to send the message if available. Error: {ex}"
        )

        _aadiscordbot_send_private_message(
            user_id=user_id,
            level=level,
            title=title,
            message=message,
            embed_message=embed_message,
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

    client = DiscordClient()

    try:
        logger.debug("Trying to send a channel message via discordproxy")

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
            "Something went wrong with discordproxy, "
            "cannot send a channel message, "
            f"trying allianceauth-discordbot to send the message. Error: {ex}"
        )

        _aadiscordbot_send_channel_message(
            channel_id=channel_id,
            level=level,
            title=title,
            message=message,
            embed_message=True,
        )


def send_user_notification(
    user: User,
    title: str,
    message: str,
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

    getattr(notify, level)(user=user, title=title, message=message)

    # Handle Discord PMs when aa_discordnotify is not active
    # Check if either allianceauth_discordbot or discordproxy are available
    # to send the PM
    if hasattr(user, "discord"):  # Check if the user has a Discord account
        logger.debug("User has a Discord account")

        # Check if discordnotify is active
        if not aa_discordnotify_installed():
            if discordproxy_installed():
                logger.debug("discordproxy seems to be available ...")

                _discordproxy_send_private_message(
                    user_id=int(user.discord.uid),
                    level=level,
                    title=title,
                    message=message,
                    embed_message=embed_message,
                )
            else:
                # discordproxy not available, try if allianceauth-discordbot is
                # available
                logger.debug(
                    "discordproxy not available to send a direct message, "
                    "let's see if we can use allianceauth-discordbot if available"
                )

                _aadiscordbot_send_private_message(
                    user_id=int(user.discord.uid),
                    level=level,
                    title=title,
                    message=message,
                    embed_message=embed_message,
                )
        else:
            logger.debug(
                "discordnotify is active, we don't have to send the PM ourself."
            )
    else:
        logger.debug("User doesn't have a Discord account, can't send any messages ...")


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
        logger.debug("discordproxy seems to be available, check if we can use it")

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
            "discordproxy not available to send the channel message, "
            "let's see if we can use allianceauth-discordbot"
        )

        _aadiscordbot_send_channel_message(
            channel_id=channel_id,
            level="info",
            title=title,
            message=message,
            embed_message=embed_message,
        )


def notify_srp_team(srp_request: SrpRequest, additional_info: str):
    """
    Send SRP request notification to the SRP teams Discord channel

    :param srp_request:
    :type srp_request:
    :param additional_info:
    :type additional_info:
    :return:
    :rtype:
    """

    srp_team_discord_channel = Setting.objects.get_setting(
        Setting.Field.SRP_TEAM_DISCORD_CHANNEL_ID
    )

    if srp_team_discord_channel is not None:
        site_base_url = site_absolute_url()
        request_code = srp_request.request_code
        character_name = srp_request.character.character_name
        ship_type = srp_request.ship.name
        zkillboard_link = srp_request.killboard_link
        additional_information = additional_info.replace(__old="@", __new="{@}")
        srp_code = srp_request.srp_link.srp_code
        srp_link = site_base_url + reverse(
            viewname="aasrp:view_srp_requests", args=[srp_code]
        )

        title = "New SRP Request"
        message = f"**Request Code:** {request_code}\n"
        message += f"**Character:** {character_name}\n"
        message += f"**Ship:** {ship_type}\n"
        message += f"**zKillboard Link:** {zkillboard_link}\n"
        message += f"**Additional Information:**\n{additional_information}\n\n"
        message += f"**SRP Code:** {srp_code}\n"
        message += f"**SRP Link:** {srp_link}\n"

        logger.info(
            "Sending SRP request notification to the SRP team channel on Discord"
        )

        send_message_to_discord_channel(
            channel_id=srp_team_discord_channel,
            title=title,
            message=message,
        )
