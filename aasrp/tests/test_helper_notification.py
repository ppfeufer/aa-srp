# Standard Library
from unittest.mock import MagicMock, patch

# Django
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

# AA SRP
from aasrp.helper.notification import notify_srp_team


class TestNotifySrpTeam(TestCase):
    """
    Test the notify_srp_team function
    """

    def test_sends_notification_when_discord_channel_is_configured(self):
        """
        Test that a notification is sent when the Discord channel is configured

        :return:
        :rtype:
        """

        srp_request = MagicMock()
        srp_request.request_code = "REQ123"
        srp_request.character.character_name = "Test Character"
        srp_request.ship.name = "Test Ship"
        srp_request.killboard_link = "https://zkillboard.com/kill/123456/"
        srp_request.srp_link.srp_code = "SRP123"

        with (
            patch("aasrp.models.Setting.objects.get_setting", return_value=123456789),
            patch(
                "aasrp.helper.notification.render_to_string",
                return_value="Rendered Message",
            ),
            patch(
                "aasrp.helper.notification.send_message_to_discord_channel"
            ) as mock_send_message,
        ):
            notify_srp_team(srp_request, "Additional Info")
            mock_send_message.assert_called_once_with(
                channel_id=123456789,
                title="New SRP Request",
                message="Rendered Message",
            )

    def test_does_not_send_notification_when_discord_channel_is_not_configured(self):
        """
        Test that no notification is sent when the Discord channel is not configured

        :return:
        :rtype:
        """

        srp_request = MagicMock()

        with (
            patch("aasrp.models.Setting.objects.get_setting", return_value=None),
            patch(
                "aasrp.discord.channel_message.send_message_to_discord_channel"
            ) as mock_send_message,
        ):
            notify_srp_team(srp_request, "Additional Info")
            mock_send_message.assert_not_called()

    def test_handles_additional_info_with_special_characters(self):
        """
        Test that additional info with special characters is handled correctly

        :return:
        :rtype:
        """

        srp_request = MagicMock()
        srp_request.request_code = "REQ123"
        srp_request.character.character_name = "Test Character"
        srp_request.ship.name = "Test Ship"
        srp_request.killboard_link = "https://zkillboard.com/kill/123456/"
        srp_request.srp_link.srp_code = "SRP123"

        with (
            patch("aasrp.models.Setting.objects.get_setting", return_value=123456789),
            patch("aasrp.helper.notification.render_to_string") as mock_render,
            patch("aasrp.helper.notification.send_message_to_discord_channel"),
        ):
            notify_srp_team(srp_request, "Info with @mention")

            view_requests_url = reverse(
                viewname="aasrp:view_srp_requests", args=["SRP123"]
            )

            mock_render.assert_called_once_with(
                template_name="aasrp/notifications/discord/srp-team.html",
                context={
                    "request_code": "REQ123",
                    "character": "Test Character",
                    "ship": "Test Ship",
                    "killboard_link": "https://zkillboard.com/kill/123456/",
                    "additional_info": "Info with {@}mention",
                    "srp_code": "SRP123",
                    "srp_link": settings.SITE_URL + view_requests_url,
                },
            )
