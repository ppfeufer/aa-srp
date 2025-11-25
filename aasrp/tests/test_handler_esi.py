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

    def test_handles_successful_operation(self):
        """
        Test that a successful ESI operation returns the expected result.

        :return:
        :rtype:
        """

        mock_operation = MagicMock()
        mock_operation.result.return_value = "success"

        response = result(mock_operation)

        self.assertEqual(response, "success")
        mock_operation.result.assert_called_once()

    def test_handles_http_not_modified_exception(self):
        """
        Test that an HTTPNotModified exception is handled correctly.

        :return:
        :rtype:
        """

        mock_operation = MagicMock()
        mock_operation.result.side_effect = HTTPNotModified(
            status_code=HTTPStatus.NOT_MODIFIED, headers={}
        )

        response = result(mock_operation)

        self.assertIsNone(response)
        mock_operation.result.assert_called_once()

    def test_handles_content_type_error(self):
        """
        Test that a ContentTypeError exception is handled correctly.

        :return:
        :rtype:
        """

        mock_operation = MagicMock()
        mock_response = MagicMock()
        mock_operation.result.side_effect = ContentTypeError(
            operation=mock_operation,
            content_type="application/json",
            message="Invalid content type",
            response=mock_response,
        )

        response = result(mock_operation)

        self.assertIsNone(response)
        mock_operation.result.assert_called_once()

    def test_returns_none_when_http_client_error_occurs(self):
        """
        Test that an HTTPClientError exception is raised correctly.

        :return:
        :rtype:
        """

        mock_operation = MagicMock()
        mock_operation.result.side_effect = HTTPClientError(
            HTTPStatus.BAD_REQUEST, headers={}, data={}
        )

        response = result(mock_operation)

        self.assertIsNone(response)
        mock_operation.result.assert_called_once()

    def test_passes_extra_parameters_to_operation(self):
        """
        Test that extra parameters are passed correctly to the ESI operation.

        :return:
        :rtype:
        """

        mock_operation = MagicMock()
        mock_operation.result.return_value = "success"

        response = result(mock_operation, use_etag=False, extra_param="value")

        self.assertEqual(response, "success")
        mock_operation.result.assert_called_once_with(
            use_etag=False,
            return_response=False,
            force_refresh=False,
            use_cache=True,
            extra_param="value",
        )
