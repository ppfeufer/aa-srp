# -*- coding: utf-8 -*-

"""
the views
"""
from aasrp.form import AaSrpLinkForm
from aasrp.models import AaSrpLink, AaSrpStatus, AaSrpRequest
from aasrp.utils import LoggerAddTag

from django.contrib.auth.decorators import login_required, permission_required

# from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from aasrp import __title__
from aasrp.app_settings import avoid_cdn

from allianceauth.services.hooks import get_extension_logger

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aasrp.basic_access")
def dashboard(request):
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
def active_srp_links_data(request) -> JsonResponse:
    data = list()

    srp_links = (
        AaSrpLink.objects.select_related("fleet_commander")
        .prefetch_related("aasrprequest_set")
        .filter(srp_status=AaSrpStatus.ACTIVE)
    )

    # srp_links = (
    #     AaSrpLink.objects.select_related("fleet_commander")
    #     .prefetch_related("aasrprequest_set")
    #     .all()
    # )

    # if not all:
    #     srp_links = srp_links.filter(srp_status=AaSrpStatus.ACTIVE)

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
                "creator": srp_link.creator.profile.main_character.character_name,
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

    requests = AaSrpRequest.objects.filter(creator=request.user)

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
                "character": srp_request.character.character_name,
                "request_time": srp_request.post_time,
                "fleet_name": srp_request.srp_link.srp_name,
                "srp_code": srp_request.srp_link.srp_code,
                "request_code": srp_request.request_code,
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

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = AaSrpLinkForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            srp_name = form.cleaned_data["srp_name"]
            fleet_time = form.cleaned_data["fleet_time"]
            fleet_doctrine = form.cleaned_data["fleet_doctrine"]

            srp_link = AaSrpLink()
            srp_link.srp_name = srp_name
            srp_link.fleet_time = fleet_time
            srp_link.fleet_doctrine = fleet_doctrine
            srp_link.srp_code = get_random_string(length=16)
            srp_link.fleet_commander = request.user.profile.main_character
            srp_link.creator = request.user
            srp_link.save()

            request.session["msg"] = [
                "success",
                "SRP Link created",
            ]

            return redirect("aasrp:dashboard")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AaSrpLinkForm()

    context = {"avoidCdn": avoid_cdn(), "form": form}

    return render(request, "aasrp/link_add.html", context)
