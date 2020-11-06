# -*- coding: utf-8 -*-

"""
the views
"""

from aasrp.models import AaSrpLink, AaSrpStatus, AaSrpRequest, AaSrpRequestStatus
from aasrp.utils import LoggerAddTag

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from aasrp import __title__
from aasrp.app_settings import avoid_cdn

from allianceauth.services.hooks import get_extension_logger

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aasrp.basic_access")
def dashboard(request, all=False):
    """
    Index view
    """

    logger.info("Module called by %s", request.user)

    context = {
        "avoidCdn": avoid_cdn(),
    }

    return render(request, "aasrp/dashboard.html", context)


@login_required
@permission_required("aasrp.basic_access")
def active_srp_links_data(request, all=False) -> JsonResponse:
    data = list()

    srp_links = (
        AaSrpLink.objects.select_related("fleet_commander")
        .prefetch_related("aasrprequest_set")
        .all()
    )

    if not all:
        srp_links = srp_links.filter(srp_status=AaSrpStatus.ACTIVE)

    # total_cost = srp_links.aggregate(total_cost=Sum("aasrprequest__payout_amount")).get(
    #     "total_cost", 0
    # )

    for srp_link in srp_links:
        aar_link = ""
        if srp_link.aar_link:
            aar_link = '<a href="{aar_link}" target="_blank">{link_text}</a>'.format(
                aar_link=srp_link.aar_link, link_text=_("Link")
            )

        data.append(
            {
                "srp_name": srp_link.srp_name,
                "srp_status": srp_link.srp_status,
                "srp_code": srp_link.srp_code,
                "fleet_commander": srp_link.fleet_commander.character_name,
                "fleet_doctrine": srp_link.fleet_doctrine,
                "fleet_time": srp_link.fleet_time,
                "aar_link": aar_link,
                "pending_requests": srp_link.pending_requests,
            }
        )

    return JsonResponse(data, safe=False)


def pending_user_srp_requests_data(request) -> JsonResponse:
    data = list()

    requests = AaSrpRequest.objects.filter(character_id=request.user.pk)

    for srp_request in requests:
        killboard_link = ""
        if srp_request.killboard_link:
            killboard_link = (
                '<a href="{zkb_link}" target="_blank">{zkb_link}</a>'.format(
                    zkb_link=srp_request.killboard_link
                )
            )

        data.append(
            {
                "request_time": srp_request.post_time,
                "fleet_name": srp_request.srp_link.srp_name,
                "srp_code": srp_request.srp_link.srp_code,
                "ship": srp_request.ship_name,
                "zkb_link": killboard_link,
                "zbk_loss_amount": srp_request.loss_amount,
                "request_status": srp_request.request_status,
                "payout_amount": srp_request.payout_amount,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.manage_srp", "aasrp.create_srp")
def srp_link_add(request):
    logger.info("Add link called by %s", request.user)

    context = {
        "avoidCdn": avoid_cdn(),
    }

    return render(request, "aasrp/link_add.html", context)
