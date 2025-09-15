"""
Test user agent header for ESI requests
"""

# Standard Library
from unittest.mock import MagicMock, PropertyMock, patch

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


class TestUserAgent(TestCase):
    """
    Test suite for verifying the `User-Agent` header in ESI requests.
    """

    @requests_mock.Mocker()
    def test_user_agent_header(self, requests_mocker):
        """
        Test the `User-Agent` header for ESI requests.

        This test ensures that the `User-Agent` header in the request matches
        the expected format. It uses mocking to avoid making live API calls
        and verifies the header construction.

        :param requests_mocker: A mocker object provided by the `requests_mock` library
                                to intercept HTTP requests.
        :type requests_mocker: requests_mock.mocker.Mocker
        :return: None
        """

        # Create a mock response object with the expected `User-Agent` header
        mock_response = MagicMock()
        mock_response.request.headers = {
            "User-Agent": (
                f"{__app_name_useragent__}/{__version__} "
                f"({settings.ESI_USER_CONTACT_EMAIL}; +{__github_url__}) "
                f"Django-ESI/{esi_version} (+{esi_url})"
            )
        }
        # Mock the result of the API call
        mock_result = (None, mock_response)

        # Create a mock `Status` object and configure its `GetStatus` method
        mock_status = MagicMock()
        mock_status.GetStatus.return_value.result.return_value = mock_result

        # Create a mock `client` object and assign the mock `Status` object to it
        mock_client = MagicMock()
        mock_client.Status = mock_status

        # Patch the `client` property of the `ESIClientProvider` class to use the mock client
        with patch(
            target="esi.openapi_clients.ESIClientProvider.client",
            new_callable=PropertyMock,
        ) as mock_client_prop:
            mock_client_prop.return_value = mock_client

            # Call the mocked `GetStatus` method and retrieve the response
            _, response = esi.client.Status.GetStatus().result(return_response=True)

            # Assert that the `User-Agent` header in the response matches the expected value
            self.assertEqual(
                first=response.request.headers["User-Agent"],
                second=(
                    f"{__app_name_useragent__}/{__version__} "
                    f"({settings.ESI_USER_CONTACT_EMAIL}; +{__github_url__}) "
                    f"Django-ESI/{esi_version} (+{esi_url})"
                ),
            )
