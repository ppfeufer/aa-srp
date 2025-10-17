"""
Providers module for setting up the ESI (EVE Swagger Interface) client.
This module initializes the ESI client with the necessary configuration
parameters such as compatibility date, user agent name, version, and URL.
"""

# Alliance Auth
from esi.openapi_clients import ESIClientProvider

# AA SRP
from aasrp import (
    __app_name_useragent__,
    __esi_compatibility_date__,
    __github_url__,
    __version__,
)

# Initialize the ESI client with the required configuration
esi = ESIClientProvider(
    # Set the compatibility date for the ESI API.
    compatibility_date=__esi_compatibility_date__,
    # Configure the user agent for the ESI client with the application name,
    # version, and GitHub URL for identification purposes.
    ua_appname=__app_name_useragent__,
    ua_version=__version__,
    ua_url=__github_url__,
    # Specify the ESI operations that this client will support.
    operations=[
        "GetUniverseTypesTypeId",
        "GetKillmailsKillmailIdKillmailHash",
        "GetInsurancePrices",
    ],
)
