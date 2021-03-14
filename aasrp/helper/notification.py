"""
notifications helper
"""

from aasrp.app_settings import (
    allianceauth_discordbot_active,
    aa_discordnotify_active,
)

from django.contrib.auth.models import User

from allianceauth.notifications import notify


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

    notify(
        user=user,
        title=title,
        level=level,
        message=message,
    )

    # send a PM to the user on Discord if allianceauth-discordbot
    # is active and not aa-discordnotify
    if allianceauth_discordbot_active() and not aa_discordnotify_active():
        import aadiscordbot.tasks

        aadiscordbot.tasks.send_direct_message_by_user_id.delay(user.pk, message)


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
        import aadiscordbot.tasks

        aadiscordbot.tasks.send_channel_message_by_discord_id.delay(
            channel_id, message, embed=embed
        )
