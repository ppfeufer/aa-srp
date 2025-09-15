"""
Providers module for setting up the ESI (EVE Swagger Interface) client.
This module initializes the ESI client with the necessary configuration
parameters such as compatibility date, user agent name, version, and URL.
"""

# Alliance Auth
# Import the ESIClientProvider class from the ESI OpenAPI clients package
from esi.openapi_clients import ESIClientProvider

# AA SRP
# Import application-specific constants from the AA SRP package
from aasrp import __app_name_useragent__  # User agent name for the application
from aasrp import __esi_compatibility_date__  # Compatibility date for the ESI API
from aasrp import __github_url__  # GitHub URL for the application
from aasrp import __version__  # Current version of the application

# Initialize the ESI client with the required configuration
esi = ESIClientProvider(
    # Set the compatibility date for the ESI API. This ensures the client
    # uses the latest supported API version as of the specified date.
    compatibility_date=__esi_compatibility_date__,
    # Configure the user agent for the ESI client with the application name,
    # version, and GitHub URL for identification purposes.
    ua_appname=__app_name_useragent__,
    ua_version=__version__,
    ua_url=__github_url__,
)
