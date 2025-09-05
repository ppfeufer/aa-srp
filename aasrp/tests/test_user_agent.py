"""
Test user agent header for ESI requests
"""

# Third Party
import requests_mock

# Django
from django.conf import settings
from django.test import TestCase

# Alliance Auth
from esi import __url__ as esi_url
from esi import __version__ as esi_version

# AA SRP
from aasrp import __app_name_useragent__, __github_url__, __version__
from aasrp.providers import esi

MODULE_PATH = "esi.clients"


@requests_mock.Mocker()
class TestUserAgent(TestCase):
    """
    Test the user agent header for ESI requests
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.status_response = {
            "players": 12345,
            "server_version": "1132976",
            "start_time": "2017-01-02T12:34:56Z",
        }

    # @patch(MODULE_PATH + ".app_settings.ESI_USER_CONTACT_EMAIL", "email@example.com")
    def test_user_agent_header(self, requests_mocker):
        """
        Test the user agent header for ESI requests

        :param requests_mocker:
        :type requests_mocker:
        :return:
        :rtype:
        """

        requests_mocker.register_uri(
            "GET", url="http://localhost", json=self.status_response
        )
        _, response = esi.client.Status.GetStatus().result(return_response=True)

        self.assertEqual(
            first=response.request.headers["User-Agent"],
            second=(
                f"{__app_name_useragent__}/{__version__} "
                f"({settings.ESI_USER_CONTACT_EMAIL}; +{__github_url__}) "
                f"Django-ESI/{esi_version} (+{esi_url})"
            ),
        )
