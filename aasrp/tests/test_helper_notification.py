# Standard Library
from unittest.mock import ANY, MagicMock, patch

# Django
from django.conf import settings
from django.urls import reverse

# AA SRP
from aasrp.helper.notification import notify_requester, notify_srp_team
from aasrp.models import SrpRequest
from aasrp.tests import BaseTestCase


class TestNotifySrpTeam(BaseTestCase):
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
        srp_request.ship_name = "Test Ship"
        srp_request.ship_id = 12345
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


class TestNotifyRequester(BaseTestCase):
    """
    Test the notify_requester function
    """

    def setUp(self):
        self.mock_requester = MagicMock()
        self.mock_reviser = MagicMock()
        self.mock_srp_request = MagicMock()

    @patch("aasrp.helper.notification.render_to_string")
    @patch("aasrp.helper.notification.send_user_notification")
    @patch("aasrp.helper.notification.get_main_character_name_from_user")
    def test_sends_notification_with_success_level(
        self,
        mock_get_main_character_name,
        mock_send_user_notification,
        mock_render_to_string,
    ):
        """
        Test that a notification is sent with success level

        :param mock_get_main_character_name:
        :type mock_get_main_character_name:
        :param mock_send_user_notification:
        :type mock_send_user_notification:
        :param mock_render_to_string:
        :type mock_render_to_string:
        :return:
        :rtype:
        """

        self.mock_srp_request.get_request_status_display.return_value = (
            SrpRequest.Status.APPROVED
        )

        mock_get_main_character_name.return_value = "Reviser Character"
        mock_render_to_string.side_effect = [
            "allianceauth_notification",
            "discord_notification",
        ]

        notify_requester(
            requester=self.mock_requester,
            reviser=self.mock_reviser,
            srp_request=self.mock_srp_request,
            comment="Test comment",
            message_level="success",
        )

        mock_get_main_character_name.assert_called_once_with(self.mock_reviser)
        mock_render_to_string.assert_any_call(
            template_name="aasrp/notifications/allianceauth/request-status-change.html",
            context=ANY,
        )
        mock_render_to_string.assert_any_call(
            template_name="aasrp/notifications/discord/request-status-change.html",
            context=ANY,
        )
        mock_send_user_notification.assert_called_once_with(
            user=self.mock_requester,
            level="success",
            title="SRP Request Approved",
            message={
                "allianceauth": "allianceauth_notification",
                "discord": "discord_notification",
            },
        )

    @patch("aasrp.helper.notification.render_to_string")
    @patch("aasrp.helper.notification.send_user_notification")
    @patch("aasrp.helper.notification.get_main_character_name_from_user")
    def test_sends_notification_with_error_level(
        self,
        mock_get_main_character_name,
        mock_send_user_notification,
        mock_render_to_string,
    ):
        self.mock_srp_request.get_request_status_display.return_value = (
            SrpRequest.Status.REJECTED
        )

        mock_get_main_character_name.return_value = "Reviser Character"
        mock_render_to_string.side_effect = [
            "allianceauth_notification",
            "discord_notification",
        ]

        notify_requester(
            requester=self.mock_requester,
            reviser=self.mock_reviser,
            srp_request=self.mock_srp_request,
            comment="Error occurred",
            message_level="error",
        )

        mock_get_main_character_name.assert_called_once_with(self.mock_reviser)
        mock_render_to_string.assert_any_call(
            template_name="aasrp/notifications/allianceauth/request-status-change.html",
            context=ANY,
        )
        mock_render_to_string.assert_any_call(
            template_name="aasrp/notifications/discord/request-status-change.html",
            context=ANY,
        )
        mock_send_user_notification.assert_called_once_with(
            user=self.mock_requester,
            level="error",
            title="SRP Request Rejected",
            message={
                "allianceauth": "allianceauth_notification",
                "discord": "discord_notification",
            },
        )
