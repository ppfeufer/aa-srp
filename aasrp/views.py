# -*- coding: utf-8 -*-

"""
the views
"""

from aasrp.models import AaSrpLink, AaSrpStatus
from aasrp.utils import LoggerAddTag

from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

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

    srp_links = (
        AaSrpLink.objects.select_related("fleet_commander")
        .prefetch_related("aasrprequest_set")
        .all()
    )

    if not all:
        srp_links = srp_links.filter(srp_status=AaSrpStatus.ACTIVE)
    else:
        logger.info("Returning all SRP requests for %s", request.user)

    total_cost = srp_links.aggregate(total_cost=Sum("aasrprequest__payout_amount")).get(
        "total_cost", 0
    )

    context = {
        "avoidCdn": avoid_cdn(),
        "srp_links": srp_links,
        "total_cost": total_cost,
    }

    return render(request, "aasrp/dashboard.html", context)


@login_required
@permission_required("aasrp.manage_srp", "aasrp.create_srp")
def srp_link_add(request):
    logger.info("Add link called by %s", request.user)

    context = {
        "avoidCdn": avoid_cdn(),
    }

    return render(request, "aasrp/link_add.html", context)
