"""
Helper functions for SRP data.

This module provides utility functions for generating HTML representations of SRP data,
localizing ISK values, and handling SRP request details. It also includes functionality
to re-add missing ship information to SRP requests.
"""

# Django
from django.utils.translation import gettext_lazy as _

# AA SRP
from aasrp.helper.icons import copy_to_clipboard_icon
from aasrp.models import SrpRequest


def request_code_html(request_code: str) -> str:
    """
    Generate HTML for displaying a request code with a copy-to-clipboard icon.

    :param request_code: The SRP request code to display.
    :type request_code: str
    :return: HTML string for the request code with a copy-to-clipboard icon.
    :rtype: str
    """

    ctc_icon = copy_to_clipboard_icon(
        data=request_code, title=_("Copy request code to clipboard")
    )

    return f"{request_code}<sup>{ctc_icon}</sup>"


def payout_amount_html(payout_amount: int) -> str:
    """
    Generate HTML for displaying a payout amount with a copy-to-clipboard icon.

    :param payout_amount: The payout amount to display.
    :type payout_amount: int
    :return: HTML string for the payout amount with a copy-to-clipboard icon.
    :rtype: str
    """

    payout_amount_ctc_icon = copy_to_clipboard_icon(
        data=str(payout_amount), title=_("Copy payout amount to clipboard")
    )

    return (
        '<span class="srp-payout d-flex justify-content-end align-items-baseline">'
        '<span class="srp-payout-tooltip"><span class="srp-payout-amount d-block">'
        f"#payout_amount_localized#</span></span><sup>{payout_amount_ctc_icon}</sup></span>"
    )


def request_fleet_details_html(srp_request: SrpRequest) -> str:
    """
    Generate HTML for displaying fleet details of an SRP request.

    :param srp_request: The SRP request object containing fleet details.
    :type srp_request: SrpRequest
    :return: HTML string for the fleet details.
    :rtype: str
    """

    l10n_srp_code = _("SRP code")
    l10n_request_code = _("Request code")

    fleet_name = f"<p>{srp_request.srp_link.srp_name}</p>"
    fleet_details = (
        '<p class="small text-muted">'
        f"{l10n_srp_code}: {srp_request.srp_link.srp_code}<br>"
        f"{l10n_request_code}: {srp_request.request_code}</p>"
    )

    return f"{fleet_name}{fleet_details}"
