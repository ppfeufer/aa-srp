"""
Test for the providers module.
"""

# Standard Library
import logging
from unittest.mock import MagicMock

# Third Party
from aiopenapi3 import ContentTypeError, RequestError

# Alliance Auth
from esi.exceptions import HTTPClientError, HTTPNotModified

# AA SRP
from aasrp import __title__
from aasrp.providers.applogger import AppLogger
from aasrp.providers.esi import ESIHandler
from aasrp.tests import BaseTestCase


class TestAppLogger(BaseTestCase):
    """
    Test the AppLogger provider.
    """

    def test_adds_prefix_to_log_message(self):
        """
        Tests that the AppLogger correctly adds a prefix to log messages.

        :return:
        :rtype:
        """

        logger = logging.getLogger("test_logger")
        app_logger = AppLogger(logger)

        with self.assertLogs("test_logger", level="INFO") as log:
            app_logger.info("This is a test message")

        self.assertIn(f"[{__title__}] This is a test message", log.output[0])

    def test_handles_empty_message(self):
        """
        Tests that the AppLogger handles an empty log message correctly.

        :return:
        :rtype:
        """

        logger = logging.getLogger("test_logger")
        app_logger = AppLogger(logger)

        with self.assertLogs("test_logger", level="INFO") as log:
            app_logger.info("")

        self.assertIn(f"[{__title__}] ", log.output[0])


class TestESIHandlerResult(BaseTestCase):
    """
    Test the ESIHandler.result method.
    """

    def test_returns_result_when_operation_succeeds(self):
        """
        Test returning an ESIHandler result.

        :return:
        :rtype:
        """

        operation = MagicMock()
        operation.operation = MagicMock(operationId="GetSomething")
        operation.result.return_value = {"data": 1}

        result = ESIHandler.result(
            operation=operation,
            use_etag=True,
            return_response=False,
            force_refresh=False,
            use_cache=True,
        )

        self.assertEqual(result, {"data": 1})
        operation.result.assert_called_once_with(
            use_etag=True, return_response=False, force_refresh=False, use_cache=True
        )

    def test_returns_result_and_response_when_return_response_true(self):
        """
        Test returning an ESIHandler result along with the response when `return_response` is set to `True`.

        :return:
        :rtype:
        """

        operation = MagicMock()
        operation.operation = MagicMock(operationId="GetSomething")
        response_obj = MagicMock()
        operation.result.return_value = ([1, 2, 3], response_obj)

        result = ESIHandler.result(
            operation=operation,
            use_etag=False,
            return_response=True,
            force_refresh=True,
            use_cache=False,
        )

        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0], [1, 2, 3])
        self.assertIs(result[1], response_obj)
        operation.result.assert_called_once_with(
            use_etag=False, return_response=True, force_refresh=True, use_cache=False
        )

    def test_returns_none_on_http_not_modified(self):
        """
        Test returns `None` on HTTP Not Modified.

        :return:
        :rtype:
        """

        operation = MagicMock()
        operation.operation = MagicMock(operationId="GetSomething")
        # HTTPNotModified requires status_code and headers
        operation.result.side_effect = HTTPNotModified(304, {})

        result = ESIHandler.result(operation=operation, return_response=False)

        self.assertIsNone(result)

    def test_returns_none_tuple_on_http_not_modified_when_return_response_true(self):
        """
        Test returns `None` on HTTP Not Modified when `return_response` is set to `True`.

        :return:
        :rtype:
        """

        operation = MagicMock()
        operation.operation = MagicMock(operationId="GetSomething")
        # HTTPNotModified requires status_code and headers
        operation.result.side_effect = HTTPNotModified(304, {})

        result = ESIHandler.result(operation=operation, return_response=True)

        self.assertEqual(result, (None, None))

    def test_returns_none_on_content_type_error(self):
        """
        Test returns `None` on content type error.

        :return:
        :rtype:
        """

        operation = MagicMock()
        operation.operation = MagicMock(operationId="GetSomething")
        # ContentTypeError requires operation, content_type, message and response
        operation.result.side_effect = ContentTypeError(
            None, "application/json", "invalid", None
        )

        result = ESIHandler.result(operation=operation)

        self.assertIsNone(result)

    def test_returns_none_on_client_or_request_error(self):
        """
        Test returns `None` on client or request error.

        :return:
        :rtype:
        """

        # HTTPClientError requires status_code, headers and data; construct with dummy values
        client_exc = HTTPClientError(500, {}, None)
        # RequestError requires operation, request, data and parameters
        request_exc = RequestError(None, None, None, None)

        for exc in (client_exc, request_exc):
            operation = MagicMock()
            operation.operation = MagicMock(operationId="GetSomething")
            operation.result.side_effect = exc

            result = ESIHandler.result(operation=operation)
            self.assertIsNone(result)

    def test_passes_extra_kwargs_to_operation_result(self):
        """
        Test passes extra kwargs to operation result.

        :return:
        :rtype:
        """

        operation = MagicMock()
        operation.operation = MagicMock(operationId="GetSomething")
        operation.result.return_value = "ok"

        result = ESIHandler.result(
            operation=operation,
            use_etag=False,
            return_response=False,
            force_refresh=True,
            use_cache=False,
            foo="bar",
        )

        self.assertEqual(result, "ok")
        operation.result.assert_called_once_with(
            use_etag=False,
            return_response=False,
            force_refresh=True,
            use_cache=False,
            foo="bar",
        )
