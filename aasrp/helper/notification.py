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


def send_user_notification(user: User, level: str, title: str, message: str) -> None:
    """
    send notification to user
    this creates a notification in Auth and a PM in Discord when either
    AA-Discordbot or AA Discord Notifications are installed
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
        # Check for allianceauth_discordbot
        if allianceauth_discordbot_active():
            # Third Party
            import aadiscordbot.tasks

            aadiscordbot.tasks.send_direct_message_by_user_id.delay(user.pk, message)

        # Try to use discordproxy if available
        else:
            try:
                # Third Party
                from discordnotify.core import COLOR_MAP
                from discordproxy.client import DiscordClient
                from discordproxy.discord_api_pb2 import Embed
                from discordproxy.exceptions import DiscordProxyException
            except ModuleNotFoundError:
                # discordproxy not available, fail silently
                pass
            else:
                if hasattr(user, "discord"):
                    client = DiscordClient()

                    footer = Embed.Footer(text=__title__)

                    embed = Embed(
                        title=str(title),
                        description=message,
                        color=COLOR_MAP.get(level, None),
                        timestamp=timezone.now().isoformat(),
                        footer=footer,
                    )

                    try:
                        client.create_direct_message(
                            user_id=int(user.discord.uid), embed=embed
                        )
                    except DiscordProxyException:
                        # something went wrong with discordproxy, fail silently
                        pass


def send_message_to_discord_channel(
    channel_id: int, message: str, embed: bool = False
) -> None:
    """
    sending a message to a discord channel
    if AA-Discordbot is installed
    :param channel_id:
    :param message:
    :param embed:
    """

    if allianceauth_discordbot_active():
        # Third Party
        import aadiscordbot.tasks

        aadiscordbot.tasks.send_channel_message_by_discord_id.delay(
            channel_id, message, embed
        )
