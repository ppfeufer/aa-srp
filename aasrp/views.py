# coding=utf-8

"""
the views
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from aasrp.helper.eve_images import get_type_render_url_from_type_id
from aasrp import __title__
from aasrp.app_settings import avoid_cdn
from aasrp.helper.character import get_formatted_character_name
from aasrp.helper.icons import (
    get_dashboard_action_icons,
    get_srp_request_status_icon,
    get_srp_request_action_icons,
)
from aasrp.form import (
    AaSrpLinkForm,
    AaSrpLinkUpdateForm,
    AaSrpRequestForm,
    AaSrpRequestPayoutForm,
    AaSrpRequestRejectForm,
)
from aasrp.managers import AaSrpManager
from aasrp.models import AaSrpLink, AaSrpRequestStatus, AaSrpStatus, AaSrpRequest
from aasrp.utils import LoggerAddTag

from eveuniverse.models import EveType

from allianceauth.eveonline.models import EveCharacter
from allianceauth.notifications import notify
from allianceauth.services.hooks import get_extension_logger

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aasrp.basic_access")
def dashboard(request: WSGIRequest, show_all_links: bool = False) -> HttpResponse:
    """
    srp dasboard
    :param request:
    :param show_all_links:
    :return:
    """

    logger_message = "Dashboard with available SRP links called by {user}".format(
        user=request.user
    )
    if show_all_links is True:
        logger_message = "Dashboard with all SRP links called by {user}".format(
            user=request.user
        )

    logger.info(logger_message)

    context = {"avoid_cdn": avoid_cdn(), "show_all_links": show_all_links}

    return render(request, "aasrp/dashboard.html", context)


@login_required
@permission_required("aasrp.basic_access")
def ajax_dashboard_srp_links_data(
    request: WSGIRequest, show_all_links: bool = False
) -> JsonResponse:
    """
    ajax request
    get all active srp links
    :param request:
    :param show_all_links:
    :return:
    """

    data = list()

    srp_links = (
        AaSrpLink.objects.select_related("fleet_commander")
        .prefetch_related("aasrprequest_set")
        .all()
    )

    if not show_all_links:
        srp_links = srp_links.filter(srp_status=AaSrpStatus.ACTIVE)

    for srp_link in srp_links:
        aar_link = ""
        if srp_link.aar_link:
            aar_link = '<a href="{aar_link}" target="_blank">{link_text}</a>'.format(
                aar_link=srp_link.aar_link, link_text=_("Link")
            )

        actions = get_dashboard_action_icons(request=request, srp_link=srp_link)

        data.append(
            {
                "srp_name": srp_link.srp_name,
                "creator": srp_link.creator.profile.main_character.character_name,
                "fleet_time": srp_link.fleet_time.replace(tzinfo=None),
                "fleet_commander": srp_link.fleet_commander.character_name,
                "fleet_doctrine": srp_link.fleet_doctrine,
                "aar_link": aar_link,
                "srp_code": srp_link.srp_code,
                "srp_costs": srp_link.total_cost,
                "srp_status": srp_link.srp_status,
                "pending_requests": srp_link.pending_requests,
                "actions": actions,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.basic_access")
def ajax_dashboard_user_srp_requests_data(request: WSGIRequest) -> JsonResponse:
    """
    ajax request
    get user srp requests
    :param request:
    :return:
    """

    data = list()

    requests = AaSrpRequest.objects.filter(creator=request.user)

    for srp_request in requests:
        killboard_link = ""
        if srp_request.killboard_link:
            ship_render_icon_html = get_type_render_url_from_type_id(
                evetype_id=srp_request.ship.id,
                evetype_name=srp_request.ship.name,
                size=32,
                as_html=True,
            )

            killboard_link = (
                '<a href="{zkb_link}" target="_blank">'
                "{ship_render_icon_html}"
                "<span>{zkb_link_text}</span>"
                "</a>".format(
                    zkb_link=srp_request.killboard_link,
                    zkb_link_text=srp_request.ship.name,
                    ship_render_icon_html=ship_render_icon_html,
                )
            )

        srp_request_status_icon = get_srp_request_status_icon(
            request=request, srp_request=srp_request
        )
        character_display = get_formatted_character_name(
            character=srp_request.character, with_portrait=True
        )
        character_sort = get_formatted_character_name(character=srp_request.character)

        data.append(
            {
                "request_time": srp_request.post_time.replace(tzinfo=None),
                "character_html": {
                    "display": character_display,
                    "sort": character_sort,
                },
                "character": srp_request.character.character_name,
                "fleet_name": srp_request.srp_link.srp_name,
                "srp_code": srp_request.srp_link.srp_code,
                "request_code": srp_request.request_code,
                "ship_html": {"display": killboard_link, "sort": srp_request.ship.name},
                "ship": srp_request.ship.name,
                "zkb_link": killboard_link,
                "zbk_loss_amount": srp_request.loss_amount,
                "payout_amount": srp_request.payout_amount,
                "request_status_icon": srp_request_status_icon,
                "request_status": srp_request.request_status,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.manage_srp", "aasrp.create_srp")
def srp_link_add(request: WSGIRequest) -> HttpResponse:
    """
    add a srp link
    :param request:
    :return:
    """

    logger.info("Add SRP link form called by %s", request.user)

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

            messages.success(
                request,
                _('SRP link "{srp_code}" created').format(srp_code=srp_link.srp_code),
            )

            return redirect("aasrp:dashboard")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = AaSrpLinkForm()

    context = {"avoid_cdn": avoid_cdn(), "form": form}

    return render(request, "aasrp/link_add.html", context)


@login_required
@permission_required("aasrp.manage_srp", "aasrp.create_srp")
def srp_link_edit(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    add or edit AAR link
    :param request:
    :param srp_code:
    :return:
    """

    logger.info(
        "Edit SRP link form for SRP code {srp_code} called by {user}".format(
            srp_code=srp_code, user=request.user
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

            messages.success(request, _("AAR link changed"))

            return redirect("aasrp:dashboard")
    else:
        form = AaSrpLinkUpdateForm(instance=srp_link)

    context = {"avoid_cdn": avoid_cdn(), "srp_code": srp_code, "form": form}

    return render(request, "aasrp/link_edit.html", context)


@login_required
@permission_required("aasrp.basic_access")
def request_srp(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    srp request
    :param request:
    :param srp_code:
    """

    logger.info(
        "SRP request form for SRP code {srp_code} called by {user}".format(
            user=request.user, srp_code=srp_code
        )
    )

    # check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            "Unable to locate SRP Fleet "
            "using SRP code {srp_code} for user {user}".format(
                srp_code=srp_code, user=request.user
            )
        )

        messages.error(
            request,
            _("Unable to locate SRP Fleet using SRP code {srp_code}").format(
                srp_code=srp_code
            ),
        )

        return redirect("aasrp:dashboard")

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)

    # check if the SRP link is still open
    if srp_link.srp_status != AaSrpStatus.ACTIVE:
        messages.error(
            request, _("This SRP link is no longer available for SRP requests.")
        )

        return redirect("aasrp:dashboard")

    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request
        form = AaSrpRequestForm(request.POST)

        logger.debug(
            "Request type POST contains valid form: {form_is_valid}".format(
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
                    request,
                    _(
                        "There is already a SRP request for this killmail. "
                        "Please check if you got the right one."
                    ),
                )

                return redirect("aasrp:dashboard")

            creator = request.user
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
                        "Your SRP request Killmail link is invalid. "
                        "Please make sure you are using http://zkillboard.com"
                    ),
                )

                return redirect("aasrp:dashboard")

            if request.user.character_ownerships.filter(
                character__character_id=str(victim_id)
            ).exists():
                srp_request__character = EveCharacter.objects.get_character_by_id(
                    victim_id
                )

                (
                    srp_request__ship,
                    created_from_esi,
                ) = EveType.objects.get_or_create_esi(id=ship_type_id)

                srp_request.character = srp_request__character
                srp_request.ship_name = srp_request__ship.name
                srp_request.ship = srp_request__ship
                srp_request.loss_amount = ship_value
                srp_request.post_time = post_time
                srp_request.request_code = get_random_string(length=16)
                srp_request.save()

                logger.info(
                    "Created SRP request on behalf of user {user_name} "
                    "(character: {character_name}) for fleet name {srp_name} "
                    "with SRP code {srp_code}".format(
                        user_name=request.user,
                        character_name=srp_request__character,
                        srp_name=srp_link.srp_name,
                        srp_code=srp_request.request_code,
                    )
                )
                messages.success(
                    request,
                    _("Submitted SRP request for your {ship}.").format(
                        ship=srp_request.ship.name
                    ),
                )

                return redirect("aasrp:dashboard")
            else:
                messages.error(
                    request,
                    _(
                        "Character {character_id} does not belong to your Auth "
                        "account. Please add this character as an alt to "
                        "your main and try again."
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
@permission_required("aasrp.manage_srp")
def complete_srp_link(request: WSGIRequest, srp_code: str):
    """
    mark an srp link as completed
    :param request:
    :param srp_code:
    """

    logger.info(
        "Complete SRP link form for SRP code {srp_code} called by {user}".format(
            srp_code=srp_code, user=request.user
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

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = AaSrpStatus.COMPLETED
    srp_link.save()

    messages.success(request, _("SRP link marked as completed"))

    return redirect("aasrp:dashboard")


@login_required
@permission_required("aasrp.manage_srp", "manage_srp_requests")
def srp_link_view_requests(request: WSGIRequest, srp_code: str) -> HttpResponse:
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

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)
    reject_form = AaSrpRequestRejectForm()

    context = {"avoid_cdn": avoid_cdn(), "srp_link": srp_link, "form": reject_form}

    return render(request, "aasrp/view_requests.html", context)


@login_required
@permission_required("aasrp.manage_srp", "manage_srp_requests")
def ajax_srp_link_view_requests_data(
    request: WSGIRequest, srp_code: str
) -> JsonResponse:
    """
    ajax request
    get datatable data
    :param request:
    """

    data = list()

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)
    srp_requests = srp_link.requests

    for srp_request in srp_requests:
        killboard_link = ""
        if srp_request.killboard_link:
            ship_render_icon_html = get_type_render_url_from_type_id(
                evetype_id=srp_request.ship.id,
                evetype_name=srp_request.ship.name,
                size=32,
                as_html=True,
            )

            killboard_link = (
                '<a href="{zkb_link}" target="_blank">'
                "{ship_render_icon_html}"
                "<span>{zkb_link_text}</span>"
                "</a>".format(
                    zkb_link=srp_request.killboard_link,
                    zkb_link_text=srp_request.ship.name,
                    ship_render_icon_html=ship_render_icon_html,
                )
            )

        requester = srp_request.creator.username
        if srp_request.creator.profile.main_character is not None:
            requester = srp_request.creator.profile.main_character.character_name

        srp_request_status_icon = get_srp_request_status_icon(
            request=request, srp_request=srp_request
        )
        srp_request_action_icons = get_srp_request_action_icons(
            request=request, srp_link=srp_link, srp_request=srp_request
        )
        character_display = get_formatted_character_name(
            character=srp_request.character, with_portrait=True
        )
        character_sort = get_formatted_character_name(character=srp_request.character)

        data.append(
            {
                "request_time": srp_request.post_time.replace(tzinfo=None),
                "requester": requester,
                "character_html": {
                    "display": character_display,
                    "sort": character_sort,
                },
                "character": srp_request.character.character_name,
                "request_code": srp_request.request_code,
                "srp_code": srp_request.srp_link.srp_code,
                "ship_html": {"display": killboard_link, "sort": srp_request.ship.name},
                "ship": srp_request.ship.name,
                "zkb_link": killboard_link,
                "zbk_loss_amount": srp_request.loss_amount,
                "payout_amount": srp_request.payout_amount,
                "request_status_icon": srp_request_status_icon,
                "actions": srp_request_action_icons,
                "request_status": srp_request.request_status,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.manage_srp")
def enable_srp_link(request: WSGIRequest, srp_code: str):
    """
    disable SRP link
    :param request:
    :param srp_code:
    """

    logger.info(
        "Enable SRP link {srp_code} called by {user}".format(
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

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)

    srp_link.srp_status = AaSrpStatus.ACTIVE
    srp_link.save()

    messages.success(
        request,
        _("SRP link {srp_code} (re-)activated.").format(srp_code=srp_code),
    )

    return redirect("aasrp:dashboard")


@login_required
@permission_required("aasrp.manage_srp")
def disable_srp_link(request: WSGIRequest, srp_code: str):
    """
    disable SRP link
    :param request:
    :param srp_code:
    """

    logger.info(
        "Disable SRP link {srp_code} called by {user}".format(
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

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)

    srp_link.srp_status = AaSrpStatus.CLOSED
    srp_link.save()

    messages.success(
        request,
        _("SRP link {srp_code} disabled.").format(srp_code=srp_code),
    )

    return redirect("aasrp:dashboard")


@login_required
@permission_required("aasrp.manage_srp")
def delete_srp_link(request: WSGIRequest, srp_code: str):
    """
    disable SRP link
    :param request:
    :param srp_code:
    """

    logger.info(
        "Delete SRP link {srp_code} called by {user}".format(
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

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)

    srp_link.delete()

    messages.success(
        request,
        _("SRP link {srp_code} deleted.").format(srp_code=srp_code),
    )

    return redirect("aasrp:dashboard")


@login_required
@permission_required("aasrp.manage_srp", "manage_srp_requests")
def ajax_srp_request_additional_information(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    srp_request = AaSrpRequest.objects.get(request_code=srp_request_code)

    requester = srp_request.creator.username
    if srp_request.creator.profile.main_character is not None:
        requester = srp_request.creator.profile.main_character.character_name

    character = get_formatted_character_name(
        character=srp_request.character,
        with_portrait=True,
    )

    killboard_link = ""
    if srp_request.killboard_link:
        ship_render_icon_html = get_type_render_url_from_type_id(
            evetype_id=srp_request.ship.id,
            evetype_name=srp_request.ship.name,
            size=32,
            as_html=True,
        )

        killboard_link = (
            '<a href="{zkb_link}" target="_blank">'
            "{ship_render_icon_html}"
            "<span>{zkb_link_text}</span>"
            "</a>".format(
                zkb_link=srp_request.killboard_link,
                zkb_link_text=srp_request.ship.name,
                ship_render_icon_html=ship_render_icon_html,
            )
        )

    data = {
        # "killboard_link": srp_request.killboard_link,
        "killboard_link": killboard_link,
        "ship_type": srp_request.ship.name,
        "request_time": srp_request.post_time,
        "requester": requester,
        "character": character,
        "additional_info": srp_request.additional_info.replace("\n", "<br>\n"),
        "reject_info": srp_request.reject_info.replace("\n", "<br>\n"),
    }

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.manage_srp", "manage_srp_requests")
def ajax_srp_request_change_payout(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    data = list()

    if request.method == "POST":
        try:
            srp_request = AaSrpRequest.objects.get(
                request_code=srp_request_code, srp_link__srp_code=srp_code
            )

            # check whether it's valid:
            form = AaSrpRequestPayoutForm(request.POST)
            if form.is_valid():
                srp_payout = form.cleaned_data["value"]

                srp_request.payout_amount = srp_payout
                srp_request.save()

                data.append({"success": True})
            else:
                data.append({"success": False})
        except AaSrpRequest.DoesNotExist:
            data.append({"success": False})

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.manage_srp", "manage_srp_requests")
def ajax_srp_request_approve(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    data = list()

    try:
        srp_request = AaSrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )

        user = srp_request.creator
        srp_payout = srp_request.payout_amount
        srp_isk_loss = srp_request.loss_amount

        if srp_payout == 0:
            srp_request.payout_amount = srp_isk_loss

        srp_request.request_status = AaSrpRequestStatus.APPROVED
        srp_request.reject_info = ""
        srp_request.save()

        notify(
            user=user,
            title=_("SRP Request Approved"),
            level="success",
            message=_(
                "Your SRP request for a {ship_name} lost during "
                "{fleet_name} has been approved.".format(
                    ship_name=srp_request.ship.name,
                    fleet_name=srp_request.srp_link.srp_name,
                )
            ),
        )

        data.append({"success": True, "message": _("SRP request has been approved")})
    except AaSrpRequest.DoesNotExist:
        data.append({"success": False})

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.manage_srp", "manage_srp_requests")
def ajax_srp_request_deny(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    data = list()

    try:
        if request.method == "POST":
            # create a form instance and populate it with data from the request
            form = AaSrpRequestRejectForm(request.POST)

            # check whether it's valid:
            if form.is_valid():
                reject_info = form.cleaned_data["reject_info"]

                srp_request = AaSrpRequest.objects.get(
                    request_code=srp_request_code, srp_link__srp_code=srp_code
                )

                user = srp_request.creator

                srp_request.payout_amount = 0
                srp_request.request_status = AaSrpRequestStatus.REJECTED
                srp_request.reject_info = reject_info
                srp_request.save()

                notify(
                    user=user,
                    title=_("SRP Request Rejected"),
                    level="danger",
                    message=_(
                        "Your SRP request for a {ship_name} lost during "
                        "{fleet_name} has been rejected.\n\nReason:\n{reject_info}".format(
                            ship_name=srp_request.ship.name,
                            fleet_name=srp_request.srp_link.srp_name,
                            reject_info=reject_info,
                        )
                    ),
                )

                data.append(
                    {"success": True, "message": _("SRP request has been rejected")}
                )
    except AaSrpRequest.DoesNotExist:
        data.append({"success": False})

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.manage_srp", "manage_srp_requests")
def ajax_srp_request_remove(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    data = list()

    try:
        srp_request = AaSrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )

        srp_request.delete()

        data.append({"success": True, "message": _("SRP request has been removed")})
    except AaSrpRequest.DoesNotExist:
        data.append({"success": False})

    return JsonResponse(data, safe=False)
