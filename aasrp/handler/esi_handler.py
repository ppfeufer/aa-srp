"""
ESI Handler Module for AA SRP
"""

# Standard Library
from typing import Any

# Third Party
from aiopenapi3 import ContentTypeError
from httpx import Response

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger
from esi.exceptions import HTTPClientError, HTTPNotModified
from esi.openapi_clients import EsiOperation

# AA SRP
from aasrp import __title__
from aasrp.providers import AppLogger

# Initialize a logger with a custom tag for the AA SRP application
logger = AppLogger(my_logger=get_extension_logger(__name__), prefix=__title__)


def result(  # pylint: disable=too-many-arguments too-many-positional-arguments
    operation: EsiOperation,
    use_etag: bool = True,
    return_response: bool = False,
    force_refresh: bool = False,
    use_cache: bool = True,
    **extra,
) -> tuple[Any, Response] | Any:
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
    :return: The result of the ESI operation, optionally with the response object.
    :rtype: tuple[Any, Response] | Any
    """

    logger.debug(f"Handling ESI operation: {operation.operation.operationId}")

    try:
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
    except HTTPClientError as exc:
        logger.error(msg=f"Error while fetching data from ESI: {str(exc)}")

        esi_result = None

    return esi_result
