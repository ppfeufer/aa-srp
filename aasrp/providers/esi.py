"""
ESI provider
"""

# Standard Library
from typing import Any

# Third Party
from aiopenapi3 import ContentTypeError
from aiopenapi3.errors import HTTPClientError, RequestError
from httpx import Response

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from esi.exceptions import HTTPNotModified
from esi.openapi_clients import ESIClientProvider, EsiOperation

# AA SRP
from aasrp import (
    __app_name_useragent__,
    __esi_compatibility_date__,
    __github_url__,
    __version__,
)
from aasrp.providers.applogger import AppLogger

logger = AppLogger(my_logger=get_extension_logger(__name__))

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
    operations=["GetKillmailsKillmailIdKillmailHash", "GetInsurancePrices"],
)


class ESIHandler:
    """
    Handler for ESI operations, providing a method to retrieve results while handling exceptions.
    """

    @classmethod
    def result(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        cls,
        operation: EsiOperation,
        use_etag: bool = True,
        return_response: bool = False,
        force_refresh: bool = False,
        use_cache: bool = True,
        **extra,
    ) -> Any | tuple[Any, Response] | None:
        """
        Retrieve the result of an ESI operation, handling HTTPNotModified exceptions.

        :param operation: The ESI operation to execute.
        :type operation: EsiOperation
        :param use_etag: Whether to use ETag for caching.
        :type use_etag: bool
        :param return_response: Whether to return the full response object.
        :type return_response: bool
        :param force_refresh: Whether to force a refresh of the data.
        :type force_refresh: bool
        :param use_cache: Whether to use cached data.
        :type use_cache: bool
        :param extra: Additional parameters to pass to the operation.
        :type extra: dict
        :return: The result of the ESI operation.
        :rtype: Any | tuple[Any, Response] | None
        """

        logger.debug(f"Handling ESI operation: {operation.operation.operationId}")
        logger.debug(
            f"Operation parameters: use_etag={use_etag}, return_response={return_response}, force_refresh={force_refresh}, use_cache={use_cache}, extra={extra}"
        )

        response: Response | None = None

        try:
            # Call operation.result differently depending on whether the caller
            # requested the raw Response object. Some implementations return a
            # single result when return_response is False and a (result, response)
            # tuple when True, so only unpack when return_response is True.
            if return_response:
                esi_result, response = operation.result(
                    use_etag=use_etag,
                    return_response=return_response,
                    force_refresh=force_refresh,
                    use_cache=use_cache,
                    **extra,
                )

                logger.debug(
                    f"ESI Response for operation: {operation.operation.operationId}: {response}"
                )
            else:
                esi_result = operation.result(
                    use_etag=use_etag,
                    return_response=return_response,
                    force_refresh=force_refresh,
                    use_cache=use_cache,
                    **extra,
                )
        except HTTPNotModified:
            logger.debug(
                f"ESI returned 304 Not Modified for operation: {operation.operation.operationId} - Skipping update."
            )

            esi_result = None
        except ContentTypeError:
            logger.warning(
                msg="ESI returned gibberish (ContentTypeError) - Skipping update."
            )

            esi_result = None
        except (HTTPClientError, RequestError) as exc:
            logger.error(msg=f"Error while fetching data from ESI: {str(exc)}")

            esi_result = None

        # If caller requested the raw response, return a tuple (result, response)
        if return_response:
            return esi_result, response

        return esi_result
