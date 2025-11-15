"""
Unit tests for the ESI handler functions in the aasrp application.
"""

# Standard Library
from http import HTTPStatus
from unittest.mock import MagicMock

# Third Party
from aiopenapi3 import ContentTypeError

# Alliance Auth
from esi.exceptions import HTTPClientError, HTTPNotModified

# AA SRP
from aasrp.handler.esi_handler import result
from aasrp.tests import BaseTestCase


class TestHandlerEsi(BaseTestCase):
    """
    Test ESI handler functions
    """

    def test_returns_result_when_operation_succeeds(self):
        """
        Test that the result function returns the expected data when the operation succeeds.

        :return:
        :rtype:
        """

        op = MagicMock()
        op.operation.operationId = "test_operation"
        op.result.return_value = {"data": "success"}

        res = result(op)

        self.assertEqual(res, {"data": "success"})

    def test_returns_cached_data_when_http_not_modified_and_cached_enabled(self):
        """
        Test that the result function returns cached data when an HTTPNotModified exception is raised and caching is enabled.

        :return:
        :rtype:
        """

        op = MagicMock()
        op.operation.operationId = "test_operation"
        op.result.side_effect = [
            HTTPNotModified(HTTPStatus.NOT_MODIFIED, {}),
            {"data": "cached"},
        ]

        res = result(op, return_cached_for_304=True)

        self.assertEqual(res, {"data": "cached"})

    def test_returns_none_when_http_not_modified_and_cached_disabled(self):
        """
        Test that the result function returns None when an HTTPNotModified exception is raised and caching is disabled.

        :return:
        :rtype:
        """

        op = MagicMock()
        op.operation.operationId = "test_operation"
        op.result.side_effect = HTTPNotModified(HTTPStatus.NOT_MODIFIED, {})

        res = result(op, return_cached_for_304=False)

        self.assertIsNone(res)

    def test_returns_none_when_content_type_error_occurs(self):
        """
        Test that the result function returns None when a ContentTypeError exception is raised.

        :return:
        :rtype:
        """

        op = MagicMock()
        op.operation.operationId = "test_operation"
        op.result.side_effect = ContentTypeError(
            op.operation, "text/plain", "Invalid content type", MagicMock()
        )

        res = result(op)

        self.assertIsNone(res)

    def test_returns_none_when_http_client_error_occurs(self):
        """
        Test that the result function returns None when an HTTPClientError exception is raised.

        :return:
        :rtype:
        """

        op = MagicMock()
        op.operation.operationId = "test_operation"
        op.result.side_effect = HTTPClientError(
            HTTPStatus.BAD_REQUEST, {}, b"Client error"
        )

        res = result(op)

        self.assertIsNone(res)
