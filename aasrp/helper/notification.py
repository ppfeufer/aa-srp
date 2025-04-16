"""
Notifications helper
"""

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.urls import reverse

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__
from aasrp.discord.channel_message import send_message_to_discord_channel
from aasrp.discord.direct_message import send_user_notification
from aasrp.models import Setting, SrpRequest

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


def notify_requester(
    requester: User,
    reviser: User,
    srp_request: SrpRequest,
    comment: str,
    message_level: str = "success",
) -> None:
    """
    Send SRP request notification to the requester

    :param requester: The user who made the SRP request
    :type requester: User
    :param reviser: The user who is revising the SRP request
    :type reviser: User
    :param srp_request: The SRP request object
    :type srp_request: SrpRequest
    :param comment: The comment made by the reviser
    :type comment: str
    :param message_level: The level of the message (success, error, info, etc. Default: success)
    :type message_level: str
    :return: None
    :rtype: None
    """

    request_status = srp_request.get_request_status_display()

    allianceauth_notification = render_to_string(
        template_name="aasrp/notifications/allianceauth/request-status-change.html",
        context={
            "ship": srp_request.ship.name,
            "status": request_status.lower(),
            "srp_code": srp_request.srp_link.srp_code,
            "request_code": srp_request.request_code,
            "reviser": reviser,
            "comment": comment,
        },
    )

    discord_notification = render_to_string(
        template_name="aasrp/notifications/discord/request-status-change.html",
        context={
            "ship": srp_request.ship.name,
            "status": request_status.lower(),
            "srp_code": srp_request.srp_link.srp_code,
            "request_code": srp_request.request_code,
            "reviser": reviser,
            "comment": comment,
        },
    )

    send_user_notification(
        user=requester,
        level=message_level,
        title=f"SRP Request {request_status}",
        message={
            "allianceauth": allianceauth_notification,
            "discord": discord_notification,
        },
    )


def notify_srp_team(srp_request: SrpRequest, additional_info: str) -> None:
    """
    Send SRP request notification to the SRP teams Discord channel

    :param srp_request: The SRP request object
    :type srp_request: SrpRequest
    :param additional_info: Additional information to be included in the notification
    :type additional_info: str
    :return: None
    :rtype: None
    """

    srp_team_discord_channel = int(
        Setting.objects.get_setting(
            setting_key=Setting.Field.SRP_TEAM_DISCORD_CHANNEL_ID
        )
    )

    if srp_team_discord_channel:
        site_base_url = settings.SITE_URL
        srp_code = srp_request.srp_link.srp_code
        srp_link = site_base_url + reverse(
            viewname="aasrp:view_srp_requests", args=[srp_code]
        )

        message = render_to_string(
            template_name="aasrp/notifications/discord/srp-team.html",
            context={
                "request_code": srp_request.request_code,
                "character": srp_request.character.character_name,
                "ship": srp_request.ship.name,
                "killboard_link": srp_request.killboard_link,
                "additional_info": additional_info.replace("@", "{@}"),
                "srp_code": srp_code,
                "srp_link": srp_link,
            },
        )

        logger.info(
            msg="Sending SRP request notification to the SRP team channel on Discord"
        )

        send_message_to_discord_channel(
            channel_id=srp_team_discord_channel,
            title="New SRP Request",
            message=message,
        )
