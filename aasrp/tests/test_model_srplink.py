"""
Unit tests for the SrpLink model.
"""

# Standard Library
from unittest.mock import MagicMock, PropertyMock, patch

# Django
from django.utils import timezone

# AA SRP
from aasrp.models import SrpLink, SrpRequest
from aasrp.tests import BaseTestCase


class TestSrpLink(BaseTestCase):
    """
    Test case for the SrpLink model.
    """

    def test_returns_total_cost_of_approved_requests(self):
        """
        Test that the total cost of approved requests is calculated correctly.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value = [
                MagicMock(payout_amount=100),
                MagicMock(payout_amount=200),
            ]

            srp_link = SrpLink()

            result = srp_link.total_cost

            self.assertEqual(result, 300)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.APPROVED
            )

    def test_returns_zero_total_cost_when_no_approved_requests_exist(self):
        """
        Test that the total cost is zero when there are no approved requests.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value = []

            srp_link = SrpLink()

            result = srp_link.total_cost

            self.assertEqual(result, 0)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.APPROVED
            )

    def test_counts_requests_by_status_correctly(self):
        """
        Test that the count of requests by status is returned correctly.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value.count.return_value = 5

            srp_link = SrpLink()
            srp_link.pk = 1

            result = srp_link._count_requests_by_status(SrpRequest.Status.PENDING)

            self.assertEqual(result, 5)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.PENDING
            )

    def test_returns_zero_for_status_with_no_requests(self):
        """
        Test that the count of requests by status returns zero when there are no requests with that status.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value.count.return_value = 0

            srp_link = SrpLink()

            result = srp_link._count_requests_by_status(SrpRequest.Status.REJECTED)

            self.assertEqual(result, 0)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.REJECTED
            )

    def test_returns_all_requests_linked_to_srp_link(self):
        """
        Test that all requests linked to the SrpLink are returned.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.all.return_value = ["request1", "request2"]

            srp_link = SrpLink()
            srp_link.pk = 1

            result = srp_link.requests

            self.assertEqual(result, ["request1", "request2"])
            mock_rels.return_value.all.assert_called_once()

    def test_returns_string_representation_of_srp_link_name(self):
        """
        Test that the string representation of the SrpLink returns the SRP name.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="Test SRP Link")

        self.assertEqual(str(srp_link), "Test SRP Link")

    def test_returns_empty_string_when_srp_name_is_empty(self):
        """
        Test that the string representation of the SrpLink returns an empty string when the SRP name is empty.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="")

        self.assertEqual(str(srp_link), "")

    def test_handles_non_ascii_characters_in_srp_name(self):
        """
        Test that the string representation of the SrpLink handles non-ASCII characters in the SRP name.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="Тестовая ссылка")

        self.assertEqual(str(srp_link), "Тестовая ссылка")

    def test_handles_whitespace_in_srp_name(self):
        """
        Test that the string representation of the SrpLink handles whitespace in the SRP name.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="   ")

        self.assertEqual(str(srp_link), "   ")

    def test_returns_total_requests_when_requests_exist(self):
        """
        Test that the total number of requests linked to the SrpLink is returned correctly when requests exist.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.count.return_value = 5

            srp_link = SrpLink()

            result = srp_link.total_requests_count

            self.assertEqual(result, 5)
            mock_rels.return_value.count.assert_called_once()

    def test_returns_zero_when_no_requests_exist(self):
        """
        Test that the total number of requests linked to the SrpLink is zero when no requests exist.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.count.return_value = 0

            srp_link = SrpLink()

            result = srp_link.total_requests_count

            self.assertEqual(result, 0)
            mock_rels.return_value.count.assert_called_once()

    def test_returns_pending_requests_count_when_requests_exist(self):
        """
        Test that the count of pending requests linked to the SrpLink is returned correctly when pending requests exist.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value.count.return_value = 3

            srp_link = SrpLink()

            result = srp_link.pending_requests_count

            self.assertEqual(result, 3)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.PENDING
            )

    def test_returns_zero_when_no_pending_requests_exist(self):
        """
        Test that the count of pending requests linked to the SrpLink is zero when no pending requests exist.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value.count.return_value = 0

            srp_link = SrpLink()

            result = srp_link.pending_requests_count

            self.assertEqual(result, 0)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.PENDING
            )

    def test_returns_approved_requests_count_when_requests_exist(self):
        """
        Test that the count of approved requests linked to the SrpLink is returned correctly when approved requests exist.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value.count.return_value = 4

            srp_link = SrpLink()

            result = srp_link.approved_requests_count

            self.assertEqual(result, 4)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.APPROVED
            )

    def test_returns_zero_when_no_approved_requests_exist(self):
        """
        Test that the count of approved requests linked to the SrpLink is zero when no approved requests exist.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value.count.return_value = 0

            srp_link = SrpLink()

            result = srp_link.approved_requests_count

            self.assertEqual(result, 0)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.APPROVED
            )

    def test_returns_rejected_requests_count_when_requests_exist(self):
        """
        Test that the count of rejected requests linked to the SrpLink is returned correctly when rejected requests exist.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value.count.return_value = 2

            srp_link = SrpLink()

            result = srp_link.rejected_requests_count

            self.assertEqual(result, 2)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.REJECTED
            )

    def test_returns_zero_when_no_rejected_requests_exist(self):
        """
        Test that the count of rejected requests linked to the SrpLink is zero when no rejected requests exist.

        :return:
        :rtype:
        """

        with patch.object(
            SrpLink, "srp_requests", new_callable=PropertyMock
        ) as mock_rels:
            mock_rels.return_value.filter.return_value.count.return_value = 0

            srp_link = SrpLink()

            result = srp_link.rejected_requests_count

            self.assertEqual(result, 0)
            mock_rels.return_value.filter.assert_called_with(
                request_status=SrpRequest.Status.REJECTED
            )

    def test_saves_srp_link_with_empty_code_generates_unique_code(self):
        """
        Test that saving an SrpLink with an empty code generates a unique code.

        :return:
        :rtype:
        """

        srp_link = SrpLink(srp_name="Test SRP", fleet_time=timezone.now(), srp_code="")
        srp_link.save()

        self.assertNotEqual(srp_link.srp_code, "")
        self.assertEqual(len(srp_link.srp_code), 16)

    def test_saves_srp_link_with_existing_code_preserves_code(self):
        """
        Test that saving an SrpLink with an existing code preserves the code.

        :return:
        :rtype:
        """

        srp_link = SrpLink(
            srp_name="Test SRP", fleet_time=timezone.now(), srp_code="EXISTINGCODE1234"
        )
        srp_link.save()

        self.assertEqual(srp_link.srp_code, "EXISTINGCODE1234")

    def test_saves_multiple_srp_links_with_empty_code_generates_unique_codes(self):
        """
        Test that saving multiple SrpLinks with empty codes generates unique codes for each link.

        :return:
        :rtype:
        """

        srp_link1 = SrpLink(
            srp_name="Test SRP 1", fleet_time=timezone.now(), srp_code=""
        )
        srp_link1.save()

        srp_link2 = SrpLink(
            srp_name="Test SRP 2", fleet_time=timezone.now(), srp_code=""
        )
        srp_link2.save()

        self.assertNotEqual(srp_link1.srp_code, srp_link2.srp_code)
        self.assertEqual(len(srp_link1.srp_code), 16)
        self.assertEqual(len(srp_link2.srp_code), 16)
