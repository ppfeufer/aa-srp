"""
notifications helper
"""


# Django
from django.contrib.auth.models import User
from django.utils import timezone

# Alliance Auth
from allianceauth.notifications import notify

# AA SRP
from aasrp import __title__
from aasrp.app_settings import aa_discordnotify_active, allianceauth_discordbot_active
from aasrp.constants import DISCORD_EMBED_COLOR_MAP


def _aadiscordbot_send_private_message(user_id: int, message: str) -> None:
    """
    Try to send a PM to a user on Discord via allianceauth-discordbot
    :param user_id:
    :param message:
    :return:
    """

    if allianceauth_discordbot_active():
        # Third Party
        import aadiscordbot.tasks

        aadiscordbot.tasks.send_direct_message_by_user_id.delay(user_id, message)


def _aadiscordbot_send_channel_message(channel_id: int, message: str) -> None:
    """
    Try to send a message to a channel on Discord via allianceauth-discordbot
    :param channel_id:
    :param message:
    :return:
    """

    if allianceauth_discordbot_active():
        # Third Party
        import aadiscordbot.tasks

        aadiscordbot.tasks.send_channel_message_by_discord_id.delay(
            channel_id, message, False
        )


def send_user_notification(user: User, level: str, title: str, message: str) -> None:
    """
    Send notification to user
    This creates a notification in Auth and a PM in Discord when either
    Discordproxy, AA-Discordbot or AA Discord Notifications is installed
    :param user:
    :param level:
    :param title:
    :param message:
    """

    notify(user=user, title=title, level=level, message=message)

    # Handle Discord PMs when aa_discordnotify is not active
    # Check if either allianceauth_discordbot or discordproxy are available
    # to send the PM
    if not aa_discordnotify_active():
        try:
            # Third Party
            from discordproxy.client import DiscordClient
            from discordproxy.discord_api_pb2 import Embed
            from discordproxy.exceptions import DiscordProxyException
        except ModuleNotFoundError:
            # discordproxy not available, try if allianceauth-discordbot is available
            _aadiscordbot_send_private_message(user.pk, f"**{title}**\n\n{message}")
        else:
            # discordproxy is available, use it,
            # if the user has a Discord account that is
            if hasattr(user, "discord"):
                client = DiscordClient()

                footer = Embed.Footer(text=__title__)

                embed = Embed(
                    title=str(title),
                    description=message,
                    color=DISCORD_EMBED_COLOR_MAP.get(level, None),
                    timestamp=timezone.now().isoformat(),
                    footer=footer,
                )

                try:
                    client.create_direct_message(
                        user_id=int(user.discord.uid), embed=embed
                    )
                except DiscordProxyException:
                    # Something went wrong with discordproxy
                    # Fail silently and try if allianceauth-discordbot is available
                    # as a last ditch effort to get the message out to Discord
                    _aadiscordbot_send_private_message(
                        user.pk, f"**{title}**\n\n{message}"
                    )


def send_message_to_discord_channel(
    channel_id: int, title: str, message: str, embed: bool = False
) -> None:
    """
    Sending a message to a discord channel
    This creates a message to the SRP Team channel on Discord when either
    Discordproxy or AA-Discordbot is installed
    :param channel_id:
    :param title:
    :param message:
    :param embed:
    """

    # Check if either allianceauth_discordbot or discordproxy are available
    # to send the channel message
    try:
        # Third Party
        from discordproxy.client import DiscordClient
        from discordproxy.discord_api_pb2 import Embed
        from discordproxy.exceptions import DiscordProxyException
    except ModuleNotFoundError:
        # discordproxy not available, try if allianceauth-discordbot is available
        _aadiscordbot_send_channel_message(channel_id, f"**{title}**\n\n{message}")
    else:
        # discordproxy is available, use it
        client = DiscordClient()

        footer = Embed.Footer(text=__title__)

        embed = Embed(
            title=title,
            description=message,
            color=DISCORD_EMBED_COLOR_MAP.get("info", None),
            timestamp=timezone.now().isoformat(),
            footer=footer,
        )

        try:
            client.create_channel_message(channel_id=channel_id, embed=embed)
        except DiscordProxyException:
            # Something went wrong with discordproxy
            # Fail silently and try if allianceauth-discordbot is available
            # as a last ditch effort to get the message out to Discord
            _aadiscordbot_send_channel_message(channel_id, f"**{title}**\n\n{message}")
