"""
Notifications helper
"""

# Django
from django.conf import settings
from django.urls import reverse

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__
from aasrp.discord.channel_message import send_message_to_discord_channel
from aasrp.models import Setting, SrpRequest

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


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
        setting_key=Setting.Field.SRP_TEAM_DISCORD_CHANNEL_ID
    )

    if srp_team_discord_channel:
        site_base_url = settings.SITE_URL
        srp_code = srp_request.srp_link.srp_code
        srp_link = site_base_url + reverse(
            viewname="aasrp:view_srp_requests", args=[srp_code]
        )

        message = (
            f"**Request Code:** {srp_request.request_code}\n"
            f"**Character:** {srp_request.character.character_name}\n"
            f"**Ship:** {srp_request.ship.name}\n"
            f"**zKillboard Link:** {srp_request.killboard_link}\n"
            f"**Additional Information:**\n{additional_info.replace('@', '{@}')}\n\n"
            f"**SRP Code:** {srp_code}\n"
            f"**SRP Link:** {srp_link}\n"
        )

        logger.info(
            msg="Sending SRP request notification to the SRP team channel on Discord"
        )

        send_message_to_discord_channel(
            channel_id=srp_team_discord_channel,
            title="New SRP Request",
            message=message,
        )
