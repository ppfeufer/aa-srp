"""
Test user agent header for ESI requests
"""

# Django
from django.conf import settings
from django.test import TestCase

# Alliance Auth
from esi import __url__ as esi_url
from esi import __version__ as esi_version

# AA SRP
from aasrp import __app_name_useragent__, __github_url__, __version__
from aasrp.providers import esi


class TestUserAgent(TestCase):
    """
    Test the user agent header for ESI requests
    """

    def test_user_agent_header(self):
        """
        Test that the user agent header is set correctly for ESI requests.

        :return:
        :rtype:
        """

        operation = esi.client.Universe.get_universe_factions()

        self.assertEqual(
            first=operation.future.request.headers["User-Agent"],
            second=(
                f"{__app_name_useragent__}/{__version__} "
                f"({settings.ESI_USER_CONTACT_EMAIL}; +{__github_url__}) "
                f"Django-ESI/{esi_version} (+{esi_url})"
            ),
        )
