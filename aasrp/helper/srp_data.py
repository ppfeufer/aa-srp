"""
Helper functions for SRP data
"""

# Django
from django.utils.translation import gettext_lazy as _

# AA SRP
from aasrp.helper.icons import copy_to_clipboard_icon
from aasrp.helper.numbers import l10n_number_format


def request_code_html(request_code: str) -> str:
    """
    Get HTML for request code with copy to clipboard icon

    :param request:
    :type request:
    :param request_code:
    :type request_code:
    :return:
    :rtype:
    """

    request_code_ctc_icon = copy_to_clipboard_icon(
        data=request_code, title=_("Copy request code to clipboard")
    )

    return f"{request_code}<sup>{request_code_ctc_icon}</sup>"


def payout_amount_html(payout_amount: int) -> str:
    """
    Get HTML for payout amount with copy to clipboard icon

    :param request:
    :type request:
    :param payout_amount:
    :type payout_amount:
    :return:
    :rtype:
    """

    payout_amount_ctc_icon = copy_to_clipboard_icon(
        data=str(payout_amount), title=_("Copy payout amount to clipboard")
    )
    payout_amount_localized = l10n_number_format(payout_amount)
    payout_field = f'<span class="srp-payout-tooltip"><span class="srp-payout-amount d-block cursor-pointer">{payout_amount_localized} ISK</span></span>'

    return f'<span class="srp-payout d-flex justify-content-end align-items-baseline">{payout_field}<sup>{payout_amount_ctc_icon}</sup></span>'


def zkillboard_loss_amount_html(loss_amount: int) -> str:
    """
    Get HTML for localized zkillboard loss amount

    :param request:
    :type request:
    :param loss_amount:
    :type loss_amount:
    :return:
    :rtype:
    """

    loss_amount_localized = l10n_number_format(loss_amount)

    return f"{loss_amount_localized} ISK"
