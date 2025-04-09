"""
Helper functions for SRP data
"""

# Django
from django.utils.translation import gettext_lazy as _

# Alliance Auth (External Libs)
from eveuniverse.models import EveType

# AA SRP
from aasrp.helper.icons import copy_to_clipboard_icon
from aasrp.helper.numbers import l10n_number_format
from aasrp.models import SrpRequest


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

    ctc_icon = copy_to_clipboard_icon(
        data=request_code, title=_("Copy request code to clipboard")
    )

    return f"{request_code}<sup>{ctc_icon}</sup>"


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

    return (
        '<span class="srp-payout d-flex justify-content-end align-items-baseline">'
        '<span class="srp-payout-tooltip"><span class="srp-payout-amount d-block cursor-pointer">'
        f"{payout_amount_localized} ISK</span></span><sup>{payout_amount_ctc_icon}</sup></span>"
    )


def localized_isk_value(loss_amount: int) -> str:
    """
    Get localized ISK value with currency symbol

    :param loss_amount:
    :type loss_amount:
    :return:
    :rtype:
    """

    return f"{l10n_number_format(loss_amount)} ISK"


def request_fleet_details_html(srp_request: SrpRequest) -> str:
    """
    Get HTML for fleet details

    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
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


def attempt_to_re_add_ship_information_to_request(
    srp_request: SrpRequest,
) -> SrpRequest:
    """
    If for some reason the ship gets removed from EveType table,
    srp_request.ship is None. In this case, we have to re-add the ship to prevent
    errors in our DataTables …

    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
    """

    srp_kill_link_id = SrpRequest.objects.get_kill_id(
        killboard_link=srp_request.killboard_link
    )

    (
        ship_type_id,
        ship_value,  # pylint: disable=unused-variable
        victim_id,  # pylint: disable=unused-variable
    ) = SrpRequest.objects.get_kill_data(kill_id=srp_kill_link_id)
    (
        srp_request__ship,
        created_from_esi,  # pylint: disable=unused-variable
    ) = EveType.objects.get_or_create_esi(id=ship_type_id)

    srp_request.ship_name = srp_request__ship.name
    srp_request.ship = srp_request__ship
    srp_request.save()

    return srp_request
