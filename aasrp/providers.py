"""
Providers module for setting up the ESI (EVE Swagger Interface) client.
This module initializes the ESI client with the necessary configuration
parameters such as compatibility date, user agent name, version, and URL.
"""

# Standard Library
import logging

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


class AppLogger(logging.LoggerAdapter):
    """
    Custom logger adapter that adds a prefix to log messages.

    Taken from the `allianceauth-app-utils` package.
    Credits to: Erik Kalkoken
    """

    def __init__(self, my_logger, prefix):
        """
        Initializes the AppLogger with a logger and a prefix.

        :param my_logger: Logger instance
        :type my_logger: logging.Logger
        :param prefix: Prefix string to add to log messages
        :type prefix: str
        """

        super().__init__(my_logger, {})

        self.prefix = prefix

    def process(self, msg, kwargs):
        """
        Prepares the log message by adding the prefix.

        :param msg: Log message
        :type msg: str
        :param kwargs: Additional keyword arguments
        :type kwargs: dict
        :return: Prefixed log message and kwargs
        :rtype: tuple
        """

        return f"[{self.prefix}] {msg}", kwargs
