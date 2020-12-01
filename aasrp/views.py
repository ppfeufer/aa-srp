# -*- coding: utf-8 -*-

"""
the views
"""

from aasrp import __title__
from aasrp.app_settings import avoid_cdn
from aasrp.view_helper import get_dashboard_action_buttons
from aasrp.form import AaSrpLinkForm, AaSrpLinkUpdateForm, AaSrpRequestForm
from aasrp.managers import AaSrpManager
from aasrp.models import AaSrpLink, AaSrpStatus, AaSrpRequest
from aasrp.utils import LoggerAddTag
from allianceauth.eveonline.models import EveCharacter

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from allianceauth.services.hooks import get_extension_logger
from allianceauth.eveonline.providers import provider

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aasrp.basic_access")
def dashboard(request, show_all_links=False) -> HttpResponse:
    """
    Index view
    """

    logger.info("Module called by {user}".format(user=request.user))

    context = {"avoid_cdn": avoid_cdn(), "show_all_links": show_all_links}

    return render(request, "aasrp/dashboard.html", context)


@login_required
@permission_required("aasrp.basic_access")
def active_srp_links_data(request, show_all_links=False) -> JsonResponse:
    data = list()

    srp_links = (
        AaSrpLink.objects.select_related("fleet_commander")
        .prefetch_related("aasrprequest_set")
        .all()
    )

    if not show_all_links:
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

        actions = get_dashboard_action_buttons(request=request, srp_link=srp_link)

        data.append(
            {
                "srp_name": srp_link.srp_name,
                "creator": srp_link.creator.profile.main_character.character_name,
                "fleet_time": srp_link.fleet_time,
                "fleet_commander": srp_link.fleet_commander.character_name,
                "fleet_doctrine": srp_link.fleet_doctrine,
                "aar_link": aar_link,
                "srp_code": srp_link.srp_code,
                "srp_status": srp_link.srp_status,
                "pending_requests": srp_link.pending_requests,
                "actions": actions,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.basic_access")
def user_srp_requests_data(request) -> JsonResponse:
    data = list()

    requests = AaSrpRequest.objects.filter(creator=request.user)

    for srp_request in requests:
        killboard_link = ""
        if srp_request.killboard_link:
            killboard_link = (
                '<a href="{zkb_link}" target="_blank">{zkb_link_text}</a>'.format(
                    zkb_link=srp_request.killboard_link, zkb_link_text=_("Link")
                )
            )

        data.append(
            {
                "request_time": srp_request.post_time,
                "character": srp_request.character.character_name,
                "fleet_name": srp_request.srp_link.srp_name,
                "srp_code": srp_request.srp_link.srp_code,
                "request_code": srp_request.request_code,
                "ship": srp_request.ship_name,
                "zkb_link": killboard_link,
                "zbk_loss_amount": srp_request.loss_amount,
                "payout_amount": srp_request.payout_amount,
                "request_status": srp_request.request_status,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.manage_srp", "aasrp.create_srp")
def srp_link_add(request) -> HttpResponse:
    logger.info("Add link called by %s", request.user)

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request
        form = AaSrpLinkForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            srp_name = form.cleaned_data["srp_name"]
            fleet_time = form.cleaned_data["fleet_time"]
            fleet_doctrine = form.cleaned_data["fleet_doctrine"]
            aar_link = form.cleaned_data["aar_link"]

            srp_link = AaSrpLink()
            srp_link.srp_name = srp_name
            srp_link.fleet_time = fleet_time
            srp_link.fleet_doctrine = fleet_doctrine
            srp_link.aar_link = aar_link
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

    context = {"avoid_cdn": avoid_cdn(), "form": form}

    return render(request, "aasrp/link_add.html", context)


@login_required
@permission_required("aasrp.manage_srp")
def srp_link_edit(request, srp_code: str) -> HttpResponse:
    logger.info("Edit link called by %s", request.user)

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data
        form = AaSrpLinkUpdateForm(request.POST, instance=srp_link)

        # check whether it's valid:
        if form.is_valid():
            aar_link = form.cleaned_data["aar_link"]

            srp_link.aar_link = aar_link
            srp_link.save()

            request.session["msg"] = [
                "success",
                "SRP Link created",
            ]

            return redirect("aasrp:dashboard")
    else:
        form = AaSrpLinkUpdateForm(instance=srp_link)

    context = {"avoid_cdn": avoid_cdn(), "srp_code": srp_code, "form": form}

    return render(request, "aasrp/link_edit.html", context)


@login_required
@permission_required("aasrp.basic_access")
def request_srp(request, srp_code: str) -> HttpResponse:
    """
    Request SRP view
    :param request:
    :param srp_code:
    """

    logger.info(
        "SRP Request for SRP code {srp_code} called by {user}".format(
            user=request.user, srp_code=srp_code
        )
    )

    # check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            "Unable to locate SRP Fleet using code {srp_code} for user {user}".format(
                srp_code=srp_code, user=request.user
            )
        )

        messages.error(
            request,
            _("Unable to locate SRP code with ID {srp_code}").format(srp_code=srp_code),
        )
        return redirect("aasrp:dashboard")

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request
        form = AaSrpRequestForm(request.POST)

        logger.debug(
            "Request type POST contains form valid: {form_is_valid}".format(
                form_is_valid=form.is_valid()
            )
        )

        # check whether it's valid:
        if form.is_valid():
            # check if the killmail was already posted
            if AaSrpRequest.objects.filter(
                killboard_link=form.cleaned_data["killboard_link"]
            ).exists():
                messages.error(
                    request, _("There is already a SRP request for this killmail.")
                )
                return redirect("aasrp:dashboard")

            creator = request.user
            srp_link = AaSrpLink.objects.get(srp_code=srp_code)
            post_time = timezone.now()

            srp_request = AaSrpRequest()
            srp_request.killboard_link = form.cleaned_data["killboard_link"]
            srp_request.additional_info = form.cleaned_data["additional_info"]
            srp_request.creator = creator
            srp_request.srp_link = srp_link

            # parse zkillboard killmail
            try:
                srp_kill_link = AaSrpManager.get_kill_id(srp_request.killboard_link)

                (ship_type_id, ship_value, victim_id) = AaSrpManager.get_kill_data(
                    srp_kill_link
                )
            except ValueError:
                # invalid killmail
                logger.debug(
                    "User {user} submitted an invalid killmail link ({killmail_link}) "
                    "or zKillboard server could not be reached".format(
                        user=request.user, killmail_link=srp_request.killboard_link
                    )
                )

                messages.error(
                    request,
                    _(
                        "Your SRP request Killmail link is invalid. Please make sure you are using zKillboard."
                    ),
                )
                return redirect("aasrp:dashboard")

            if request.user.character_ownerships.filter(
                character__character_id=str(victim_id)
            ).exists():
                srp_request__character = EveCharacter.objects.get_character_by_id(
                    victim_id
                )

                srp_request.character = srp_request__character
                srp_request.ship_name = provider.get_itemtype(ship_type_id).name
                srp_request.loss_amount = ship_value
                srp_request.post_time = post_time
                srp_request.request_code = get_random_string(length=16)
                srp_request.save()

                logger.info(
                    "Created SRP Request on behalf of user %s for fleet name %s"
                    % (request.user, srp_link.srp_name)
                )
                messages.success(
                    request,
                    _("Submitted SRP request for your {ship}.").format(
                        ship=srp_request.ship_name
                    ),
                )
                return redirect("aasrp:dashboard")
            else:
                messages.error(
                    request,
                    _(
                        "Character {character_id} does not belong to your Auth account. "
                        "Please add the API key for this character and try again"
                    ).format(character_id=victim_id),
                )

            return redirect("aasrp:dashboard")

    # if a GET (or any other method) we'll create a blank form
    else:
        logger.debug(
            "Returning blank SRP request form for {user}".format(user=request.user)
        )

        form = AaSrpRequestForm()

    context = {"avoid_cdn": avoid_cdn(), "srp_code": srp_code, "form": form}

    return render(request, "aasrp/request_srp.html", context)


@login_required
@permission_required("aasrp.manage_srp", "manage_srp_requests")
def srp_link_view_requests(request, srp_code: str) -> HttpResponse:
    """
    view srp requests for a specific srp code
    :param request:
    :param srp_code:
    """

    logger.info(
        "View SRP request for SRP code {srp_code} called by {user}".format(
            user=request.user, srp_code=srp_code
        )
    )

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)

    context = {"avoid_cdn": avoid_cdn(), "srp_link": srp_link}

    return render(request, "aasrp/view_requests.html", context)


@login_required
@permission_required("aasrp.basic_access")
def srp_link_view_requests_data(request) -> JsonResponse:
    """
    get datatable data
    :param request:
    """
