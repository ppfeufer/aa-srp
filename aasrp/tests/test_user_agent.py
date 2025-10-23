"""
Test user agent header for ESI requests
"""

# Standard Library
from unittest.mock import MagicMock, patch

# Third Party
import httpx

# Django
from django.conf import settings

# Alliance Auth
from esi import __url__ as esi_url
from esi import __version__ as esi_version
from esi.openapi_clients import ESIClientProvider
from esi.tests.test_openapi import SPEC_PATH

# AA SRP
from aasrp import (
    __app_name_useragent__,
    __esi_compatibility_date__,
    __github_url__,
    __version__,
)
from aasrp.tests import BaseTestCase


class TestUserAgent(BaseTestCase):
    """
    Test suite for verifying the `User-Agent` header in ESI requests.
    """

    @patch.object(httpx.Client, "send")
    def test_user_agent_header(self, send: MagicMock):
        """
        Test that the `User-Agent` header is correctly set in ESI requests.

        This test verifies that the `User-Agent` header in HTTP requests made by the ESI client
        is constructed correctly based on the provided application name, version, and other metadata.

        Args:
            send (MagicMock): A mocked `httpx.Client.send` method to intercept HTTP requests and provide a controlled response.

        Assertions:
            - The `User-Agent` header in the HTTP request matches the expected format.
            - The `players` field in the response JSON is correctly parsed and matches the expected value.
        """

        # Initialize the ESI client provider with test-specific metadata
        esi = ESIClientProvider(
            ua_appname=__app_name_useragent__,  # Application name for the User-Agent header
            ua_url=__github_url__,  # Application URL for the User-Agent header
            ua_version=__version__,  # Application version for the User-Agent header
            compatibility_date=__esi_compatibility_date__,  # Compatibility date for the ESI spec
            spec_file=SPEC_PATH,  # Path to the OpenAPI specification file
        )

        # Mock the HTTP response returned by the `send` method
        send.return_value = httpx.Response(
            status_code=200,  # HTTP status code for the response
            json={  # Mocked JSON response body
                "players": 1234,
                "server_version": "1234",
                "start_time": "2029-09-19T11:02:08Z",
            },
            request=httpx.Request(method="GET", url="test"),  # Mocked HTTP request
        )

        # Perform the ESI client request and retrieve the status
        status = esi.client.Status.GetStatus().result()

        # Retrieve the arguments passed to the mocked `send` method
        call_args, call_kwargs = send.call_args

        # Assert that the `User-Agent` header matches the expected format
        self.assertEqual(
            first=call_args[0].headers["user-agent"],
            second=(
                f"AaSrp/{__version__} "
                f"({settings.ESI_USER_CONTACT_EMAIL}; +{__github_url__}) "
                f"DjangoEsi/{esi_version} (+{esi_url})"
            ),
        )

        # Assert that the `players` field in the response matches the expected value
        self.assertEqual(first=status.players, second=1234)
