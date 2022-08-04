"""
The views
"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import reverse_absolute, site_absolute_url
from eveuniverse.models import EveType

# AA SRP
from aasrp import __title__
from aasrp.app_settings import AASRP_SRP_TEAM_DISCORD_CHANNEL
from aasrp.constants import SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE, ZKILLBOARD_BASE_URL
from aasrp.form import (
    AaSrpLinkForm,
    AaSrpLinkUpdateForm,
    AaSrpRequestAcceptForm,
    AaSrpRequestAcceptRejectedForm,
    AaSrpRequestForm,
    AaSrpRequestPayoutForm,
    AaSrpRequestRejectForm,
    AaSrpUserSettingsForm,
)
from aasrp.helper.character import (
    get_formatted_character_name,
    get_main_character_from_user,
)
from aasrp.helper.eve_images import get_type_render_url_from_type_id
from aasrp.helper.icons import (
    get_dashboard_action_icons,
    get_srp_request_action_icons,
    get_srp_request_details_icon,
    get_srp_request_status_icon,
)
from aasrp.helper.notification import (
    send_message_to_discord_channel,
    send_user_notification,
)
from aasrp.managers import AaSrpManager
from aasrp.models import (
    AaSrpInsurance,
    AaSrpLink,
    AaSrpRequest,
    AaSrpRequestComment,
    AaSrpUserSettings,
)

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


def _attempt_to_re_add_ship_information_to_request(
    srp_request: AaSrpRequest,
) -> AaSrpRequest:
    """
    If for some reason the ship gets removed from EveType table,
    srp_request.ship is None. In this case, we have to re-add the ship to prevent
    errors in our DataTables ...
    :param srp_request:
    :return:
    """

    srp_kill_link = AaSrpManager.get_kill_id(srp_request.killboard_link)

    (ship_type_id, ship_value, victim_id) = AaSrpManager.get_kill_data(srp_kill_link)
    (srp_request__ship, created_from_esi) = EveType.objects.get_or_create_esi(
        id=ship_type_id
    )

    srp_request.ship_name = srp_request__ship.name
    srp_request.ship = srp_request__ship
    srp_request.save()

    return srp_request


@login_required
@permission_required("aasrp.basic_access")
def dashboard(request: WSGIRequest, show_all_links: bool = False) -> HttpResponse:
    """
    SRP dashboard
    :param request:
    :param show_all_links:
    :return:
    """

    # Check if the current user has any settings. if not, create the default set
    try:
        user_settings = AaSrpUserSettings.objects.get(user=request.user)
    except AaSrpUserSettings.DoesNotExist:
        # create the default settings in the DB for the current user
        user_settings = AaSrpUserSettings(user=request.user)
        user_settings.save()

    # If this is a POST request we need to process the form data
    if request.method == "POST":
        user_settings_form = AaSrpUserSettingsForm(request.POST, instance=user_settings)

        # Check whether it's valid:
        if user_settings_form.is_valid():
            user_settings.disable_notifications = user_settings_form.cleaned_data[
                "disable_notifications"
            ]
            user_settings.save()
    else:
        user_settings_form = AaSrpUserSettingsForm(instance=user_settings)

    logger_message = f"Dashboard with available SRP links called by {request.user}"

    if show_all_links is True:
        if not request.user.has_perm("aasrp.manage_srp"):
            messages.error(
                request,
                _("You do not have the needed permissions to view all SRP links"),
            )

            return redirect("aasrp:dashboard")

        logger_message = f"Dashboard with all SRP links called by {request.user}"

    logger.info(logger_message)

    context = {
        "show_all_links": show_all_links,
        "user_settings_form": user_settings_form,
    }

    return render(request, "aasrp/dashboard.html", context)


@login_required
@permission_required("aasrp.basic_access")
def ajax_dashboard_srp_links_data(
    request: WSGIRequest, show_all_links: bool = False
) -> JsonResponse:
    """
    Ajax request :: Get all active SRP links
    :param request:
    :param show_all_links:
    :return:
    """

    data = []

    srp_links = AaSrpLink.objects.prefetch_related(
        "fleet_commander",
        "creator",
        "creator__profile__main_character",
        "srp_requests",
    ).all()

    if not show_all_links:
        srp_links = srp_links.filter(srp_status=AaSrpLink.Status.ACTIVE)

    for srp_link in srp_links:
        aar_link = ""
        if srp_link.aar_link:
            aar_href = srp_link.aar_link
            link_text = _("Link")
            aar_link = f'<a href="{aar_href}" target="_blank">{link_text}</a>'

        srp_code_html = srp_link.srp_code
        if srp_link.srp_status == AaSrpLink.Status.ACTIVE:
            css_classes = (
                "aa-srp-fa-icon aa-srp-fa-icon-right copy-text-fa-icon far fa-copy"
            )
            srp_link_href = reverse_absolute(
                "aasrp:request_srp", args=[srp_link.srp_code]
            )
            title = _("Copy SRP link to clipboard")
            srp_code_html += (
                f'<i class="{css_classes}" '
                f'data-clipboard-text="{srp_link_href}" title="{title}"></i>'
            )

        actions = get_dashboard_action_icons(request=request, srp_link=srp_link)

        data.append(
            {
                "srp_name": srp_link.srp_name,
                "creator": get_main_character_from_user(srp_link.creator),
                "fleet_time": srp_link.fleet_time,
                "fleet_commander": srp_link.fleet_commander.character_name,
                "fleet_doctrine": srp_link.fleet_doctrine,
                "aar_link": aar_link,
                "srp_code": {"display": srp_code_html, "sort": srp_link.srp_code},
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
    Ajax request :: Get user srp requests
    :param request:
    :return:
    """

    data = []

    requests = (
        AaSrpRequest.objects.filter(creator=request.user)
        # .filter(ship__isnull=False)
        .prefetch_related(
            "creator",
            "creator__profile__main_character",
            "character",
            "srp_link",
            "srp_link__creator",
            "srp_link__creator__profile__main_character",
            "ship",
        )
    )

    for srp_request in requests:
        killboard_link = ""

        if srp_request.killboard_link:
            try:
                ship_render_icon_html = get_type_render_url_from_type_id(
                    evetype_id=srp_request.ship_id,
                    evetype_name=srp_request.ship.name,
                    size=32,
                    as_html=True,
                )
            except AttributeError:
                # For some reason it seems the ship has been removed from EveType
                # table, attempt to add it again ...
                srp_request = _attempt_to_re_add_ship_information_to_request(
                    srp_request
                )

                ship_render_icon_html = get_type_render_url_from_type_id(
                    evetype_id=srp_request.ship_id,
                    evetype_name=srp_request.ship.name,
                    size=32,
                    as_html=True,
                )

            zkb_link = srp_request.killboard_link
            zkb_link_text = srp_request.ship.name
            killboard_link = (
                f'<a href="{zkb_link}" target="_blank">'
                f"{ship_render_icon_html}"
                f"<span>{zkb_link_text}</span>"
                "</a>"
            )

        srp_request_status_icon = get_srp_request_status_icon(
            request=request, srp_request=srp_request
        )

        srp_request_details_icon = get_srp_request_details_icon(
            request=request, srp_link=srp_request.srp_link, srp_request=srp_request
        )

        character_display = get_formatted_character_name(
            character=srp_request.character, with_portrait=True
        )
        character_sort = get_formatted_character_name(character=srp_request.character)

        data.append(
            {
                "request_time": srp_request.post_time,
                "character_html": {
                    "display": character_display,
                    "sort": character_sort,
                },
                "character": srp_request.character.character_name,
                "fleet_name": srp_request.srp_link.srp_name,
                "srp_code": srp_request.srp_link.srp_code,
                "request_code": srp_request.request_code,
                "ship_html": {
                    "display": killboard_link,
                    "sort": srp_request.ship.name,
                },
                "ship": srp_request.ship.name,
                "zkb_link": killboard_link,
                "zbk_loss_amount": srp_request.loss_amount,
                "payout_amount": srp_request.payout_amount,
                "request_status_icon": (
                    srp_request_details_icon + srp_request_status_icon
                ),
                "request_status": srp_request.request_status,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.create_srp"))
def srp_link_add(request: WSGIRequest) -> HttpResponse:
    """
    Add a SRP link
    :param request:
    :return:
    """

    logger.info("Add SRP link form called by %s", request.user)

    # If this is a POST request we need to process the form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = AaSrpLinkForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            srp_name = form.cleaned_data["srp_name"]
            fleet_time = form.cleaned_data["fleet_time"]
            fleet_doctrine = form.cleaned_data["fleet_doctrine"]
            aar_link = form.cleaned_data["aar_link"]

            srp_link = AaSrpLink(
                srp_name=srp_name,
                fleet_time=fleet_time,
                fleet_doctrine=fleet_doctrine,
                aar_link=aar_link,
                srp_code=get_random_string(length=16),
                fleet_commander=request.user.profile.main_character,
                creator=request.user,
            )
            srp_link.save()

            messages.success(
                request,
                _(f'SRP link "{srp_link.srp_code}" created'),
            )

            return redirect("aasrp:dashboard")

    # If a GET (or any other method) we'll create a blank form
    else:
        form = AaSrpLinkForm()

    context = {"form": form}

    return render(request, "aasrp/link_add.html", context)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.create_srp"))
def srp_link_edit(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    Add or edit AAR link
    :param request:
    :param srp_code:
    :return:
    """

    request_user = request.user

    logger.info(f"Edit SRP link form for SRP code {srp_code} called by {request_user}")

    # Check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request_user}"
        )

        messages.error(
            request,
            _(f"Unable to locate SRP code with ID {srp_code}"),
        )

        return redirect("aasrp:dashboard")

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)

    # If this is a POST request we need to process the form data
    if request.method == "POST":
        # Create a form instance and populate it with data
        form = AaSrpLinkUpdateForm(request.POST, instance=srp_link)

        # Check whether it's valid:
        if form.is_valid():
            aar_link = form.cleaned_data["aar_link"]

            srp_link.aar_link = aar_link
            srp_link.save()

            messages.success(request, _("AAR link changed"))

            return redirect("aasrp:dashboard")
    else:
        form = AaSrpLinkUpdateForm(instance=srp_link)

    context = {"srp_code": srp_code, "form": form}

    return render(request, "aasrp/link_edit.html", context)


@login_required
@permission_required("aasrp.basic_access")
def request_srp(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    SRP request
    :param request:
    :param srp_code:
    """

    request_user = request.user

    logger.info(f"SRP request form for SRP code {srp_code} called by {request_user}")

    # Check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using SRP code {srp_code} for "
            f"user {request_user}"
        )

        messages.error(
            request, _(f"Unable to locate SRP Fleet using SRP code {srp_code}")
        )

        return redirect("aasrp:dashboard")

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)

    # Check if the SRP link is still open
    if srp_link.srp_status != AaSrpLink.Status.ACTIVE:
        messages.error(
            request, _("This SRP link is no longer available for SRP requests.")
        )

        return redirect("aasrp:dashboard")

    # If this is a POST request we need to process the form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = AaSrpRequestForm(request.POST)
        form_is_valid = form.is_valid()

        logger.debug(f"Request type POST contains valid form: {form_is_valid}")

        # Check whether it's valid:
        if form.is_valid():
            creator = request.user
            post_time = timezone.now()
            submitted_killmail_link = form.cleaned_data["killboard_link"]

            # Parse killmail
            try:
                srp_kill_link = AaSrpManager.get_kill_id(submitted_killmail_link)

                (ship_type_id, ship_value, victim_id) = AaSrpManager.get_kill_data(
                    srp_kill_link
                )
            except ValueError:
                # Invalid killmail
                logger.debug(
                    f"User {request_user} submitted an invalid killmail link "
                    f"({submitted_killmail_link}) or zKillboard server could "
                    "not be reached"
                )

                messages.error(
                    request,
                    _(
                        "Your SRP request Killmail link is invalid. "
                        f"Please make sure you are using {ZKILLBOARD_BASE_URL}"
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

                srp_request = AaSrpRequest(
                    killboard_link=submitted_killmail_link,
                    creator=creator,
                    srp_link=srp_link,
                    character=srp_request__character,
                    ship_name=srp_request__ship.name,
                    ship=srp_request__ship,
                    loss_amount=ship_value,
                    post_time=post_time,
                    request_code=get_random_string(length=16),
                )
                srp_request.save()

                # Save Request Create Even in request history
                AaSrpRequestComment(
                    srp_request=srp_request,
                    comment_type=AaSrpRequestComment.Type.REQUEST_ADDED,
                    creator=creator,
                    new_status=AaSrpRequest.Status.PENDING,
                ).save()

                # Add request info to request history
                srp_request_additional_info = form.cleaned_data["additional_info"]
                AaSrpRequestComment(
                    comment=srp_request_additional_info,
                    srp_request=srp_request,
                    comment_type=AaSrpRequestComment.Type.REQUEST_INFO,
                    creator=creator,
                ).save()

                # Add insurance information
                insurance_information = AaSrpManager.get_insurance_for_ship_type(
                    ship_type_id=ship_type_id
                )

                for insurance_level in insurance_information["levels"]:
                    logger.debug(insurance_level)

                    insurance = AaSrpInsurance(
                        srp_request=srp_request,
                        insurance_level=insurance_level["name"],
                        insurance_cost=insurance_level["cost"],
                        insurance_payout=insurance_level["payout"],
                    )
                    insurance.save()

                user_name = request.user
                character_name = srp_request__character
                srp_name = srp_link.srp_name
                srp_code = srp_request.request_code
                logger.info(
                    f"Created SRP request on behalf of user {user_name} "
                    f"(character: {character_name}) for fleet name {srp_name} "
                    f"with SRP code {srp_code}"
                )

                ship = srp_request.ship.name
                messages.success(request, _(f"Submitted SRP request for your {ship}."))

                # Send message to the srp team in their discord channel
                if AASRP_SRP_TEAM_DISCORD_CHANNEL is not None:
                    site_base_url = site_absolute_url()
                    request_code = srp_request.request_code
                    character_name = srp_request__character.character_name
                    ship_type = srp_request__ship.name
                    zkillboard_link = srp_request.killboard_link
                    additional_information = srp_request_additional_info.replace(
                        "@", "{@}"
                    )
                    srp_link = site_base_url + reverse(
                        "aasrp:view_srp_requests", args=[srp_link.srp_code]
                    )

                    title = "New SRP Request"
                    message = f"**Request Code:** {request_code}\n"
                    message += f"**Character:** {character_name}\n"
                    message += f"**Ship:** {ship_type}\n"
                    message += f"**zKillboard Link:** {zkillboard_link}\n"
                    message += (
                        f"**Additional Information:**\n{additional_information}\n\n"
                    )
                    message += f"**SRP Code:** {srp_code}\n"
                    message += f"**SRP Link:** {srp_link}\n"

                    logger.info(
                        "Sending SRP request notification to the SRP team channel on "
                        "Discord"
                    )

                    send_message_to_discord_channel(
                        channel_id=AASRP_SRP_TEAM_DISCORD_CHANNEL,
                        title=title,
                        message=message,
                    )

                return redirect("aasrp:dashboard")

            messages.error(
                request,
                _(
                    f"Character {victim_id} does not belong to your Auth "
                    "account. Please add this character as an alt to "
                    "your main and try again."
                ),
            )

            return redirect("aasrp:dashboard")

    # If a GET (or any other method) we'll create a blank form
    else:
        logger.debug(f"Returning blank SRP request form for {request.user}")

        form = AaSrpRequestForm()

    context = {"srp_code": srp_code, "form": form}

    return render(request, "aasrp/request_srp.html", context)


@login_required
@permission_required("aasrp.manage_srp")
def complete_srp_link(request: WSGIRequest, srp_code: str):
    """
    Mark an SRP link as completed
    :param request:
    :param srp_code:
    """

    logger.info(
        f"Complete SRP link form for SRP code {srp_code} called by {request.user}"
    )

    # check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = AaSrpLink.Status.COMPLETED
    srp_link.save()

    messages.success(request, _("SRP link marked as completed"))

    return redirect("aasrp:dashboard")


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_link_view_requests(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    View SRP requests for a specific SRP code
    :param request:
    :param srp_code:
    """

    logger.info(f"View SRP request for SRP code {srp_code} called by {request.user}")

    # Check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)
    reject_form = AaSrpRequestRejectForm()
    accept_form = AaSrpRequestAcceptForm()
    accept_rejected_form = AaSrpRequestAcceptRejectedForm()

    context = {
        "srp_link": srp_link,
        "forms": {
            "reject_request": reject_form,
            "accept_request": accept_form,
            "accept_rejected_request": accept_rejected_form,
        },
    }

    return render(request, "aasrp/view_requests.html", context)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def ajax_srp_link_view_requests_data(
    request: WSGIRequest, srp_code: str
) -> JsonResponse:
    """
    Ajax request :: Get datatable data
    :param srp_code:
    :param request:
    """

    data = []

    srp_requests = AaSrpRequest.objects.filter(
        srp_link__srp_code__iexact=srp_code
    ).prefetch_related(
        "srp_link",
        "srp_link__creator",
        "srp_link__creator__profile__main_character",
        "character",
        "ship",
    )

    for srp_request in srp_requests:
        killboard_link = ""
        if srp_request.killboard_link:
            try:
                ship_render_icon_html = get_type_render_url_from_type_id(
                    evetype_id=srp_request.ship_id,
                    evetype_name=srp_request.ship.name,
                    size=32,
                    as_html=True,
                )
            except AttributeError:
                # For some reason it seems the ship has been removed from EveType
                # table, attempt to add it again ...
                srp_request = _attempt_to_re_add_ship_information_to_request(
                    srp_request
                )

                ship_render_icon_html = get_type_render_url_from_type_id(
                    evetype_id=srp_request.ship_id,
                    evetype_name=srp_request.ship.name,
                    size=32,
                    as_html=True,
                )

            killboard_link = (
                f'<a href="{srp_request.killboard_link}" target="_blank">'
                f"{ship_render_icon_html}"
                f"<span>{srp_request.ship.name}</span></a>"
            )

        srp_request_status_icon = get_srp_request_status_icon(
            request=request, srp_request=srp_request
        )
        srp_request_action_icons = get_srp_request_action_icons(
            request=request, srp_link=srp_request.srp_link, srp_request=srp_request
        )
        character_display = get_formatted_character_name(
            character=srp_request.character, with_portrait=True, with_copy_icon=True
        )
        character_sort = get_formatted_character_name(character=srp_request.character)

        data.append(
            {
                "request_time": srp_request.post_time,
                "requester": get_main_character_from_user(srp_request.creator),
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
    Enable SRP link
    :param request:
    :param srp_code:
    """

    logger.info(f"Enable SRP link {srp_code} called by {request.user}")

    # Check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = AaSrpLink.Status.ACTIVE
    srp_link.save()

    messages.success(request, _(f"SRP link {srp_code} (re-)activated."))

    return redirect("aasrp:dashboard")


@login_required
@permission_required("aasrp.manage_srp")
def disable_srp_link(request: WSGIRequest, srp_code: str):
    """
    Disable SRP link
    :param request:
    :param srp_code:
    """

    logger.info(f"Disable SRP link {srp_code} called by {request.user}")

    # Check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = AaSrpLink.Status.CLOSED
    srp_link.save()

    messages.success(request, _(f"SRP link {srp_code} disabled."))

    return redirect("aasrp:dashboard")


@login_required
@permission_required("aasrp.manage_srp")
def delete_srp_link(request: WSGIRequest, srp_code: str):
    """
    Delete SRP link
    :param request:
    :param srp_code:
    """

    logger.info(f"Delete SRP link {srp_code} called by {request.user}")

    # check if the provided SRP code is valid
    if AaSrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = AaSrpLink.objects.get(srp_code=srp_code)
    srp_link.delete()

    messages.success(request, _(f"SRP link {srp_code} deleted."))

    return redirect("aasrp:dashboard")


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def ajax_srp_request_additional_information(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> HttpResponse:
    """
    Ajax Call :: Get additional information for an SRP request
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    srp_request = AaSrpRequest.objects.get(
        srp_link__srp_code=srp_code, request_code=srp_request_code
    )

    insurance_information = srp_request.insurance.filter(srp_request=srp_request)

    character = get_formatted_character_name(
        character=srp_request.character, with_portrait=True
    )

    try:
        ship_render_icon_html = get_type_render_url_from_type_id(
            evetype_id=srp_request.ship_id,
            evetype_name=srp_request.ship.name,
            size=32,
            as_html=True,
        )
    except AttributeError:
        # For some reason it seems the ship has been removed from EveType
        # table, attempt to add it again ...
        srp_request = _attempt_to_re_add_ship_information_to_request(srp_request)

        ship_render_icon_html = get_type_render_url_from_type_id(
            evetype_id=srp_request.ship_id,
            evetype_name=srp_request.ship.name,
            size=32,
            as_html=True,
        )

    request_status_banner_alert_level = "info"
    if srp_request.request_status == AaSrpRequest.Status.APPROVED:
        request_status_banner_alert_level = "success"

    if srp_request.request_status == AaSrpRequest.Status.REJECTED:
        request_status_banner_alert_level = "danger"

    try:
        additional_info_comment = AaSrpRequestComment.objects.get(
            srp_request=srp_request, comment_type=AaSrpRequestComment.Type.REQUEST_INFO
        )

        additional_info = additional_info_comment.comment.replace("\n", "<br>\n")
    except AaSrpRequestComment.DoesNotExist:
        additional_info = ""

    try:
        request_history = AaSrpRequestComment.objects.filter(
            ~Q(comment_type=AaSrpRequestComment.Type.REQUEST_INFO),
            srp_request=srp_request,
        ).order_by("pk")
    except AaSrpRequestComment.DoesNotExist:
        request_history = ""

    data = {
        "srp_request": srp_request,
        "ship_render_icon_html": ship_render_icon_html,
        "ship_type": srp_request.ship.name,
        "requester": get_main_character_from_user(srp_request.creator),
        "character": character,
        "additional_info": additional_info,
        "request_status_banner_alert_level": request_status_banner_alert_level,
        "request_status": srp_request.request_status,
        "insurance_information": insurance_information,
        "request_history": request_history,
    }

    return render(
        request, "aasrp/ajax_render/srp_request_additional_information.html", data
    )


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def ajax_srp_request_change_payout(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Ajax call :: Change SRP payout
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    data = []

    if request.method == "POST":
        try:
            srp_request = AaSrpRequest.objects.get(
                request_code=srp_request_code, srp_link__srp_code=srp_code
            )
        except AaSrpRequest.DoesNotExist:
            data.append({"success": False})
        else:
            # check whether it's valid:
            form = AaSrpRequestPayoutForm(request.POST)
            if form.is_valid():
                srp_payout = form.cleaned_data["value"]

                srp_request.payout_amount = srp_payout
                srp_request.save()

                data.append({"success": True})
            else:
                data.append({"success": False})

    return JsonResponse(data, safe=False)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def ajax_srp_request_approve(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Ajax call :: Approve SRP request
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    data = []

    try:
        srp_request = AaSrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )
    except AaSrpRequest.DoesNotExist:
        data.append({"success": False})
    else:
        if request.method == "POST":
            # Create a form instance and populate it with data from the request
            form = None

            if srp_request.request_status == AaSrpRequest.Status.PENDING:
                form = AaSrpRequestAcceptForm(request.POST)
            elif srp_request.request_status == AaSrpRequest.Status.REJECTED:
                form = AaSrpRequestAcceptRejectedForm(request.POST)

            if form and form.is_valid():
                requester = srp_request.creator
                srp_payout = srp_request.payout_amount
                srp_isk_loss = srp_request.loss_amount

                # Reviser comment
                reviser_comment = form.cleaned_data["reviser_comment"]

                if srp_payout == 0:
                    srp_request.payout_amount = srp_isk_loss

                # Set new status in request history
                AaSrpRequestComment(
                    srp_request=srp_request,
                    comment_type=AaSrpRequestComment.Type.STATUS_CHANGE,
                    new_status=AaSrpRequest.Status.APPROVED,
                    creator=request.user,
                ).save()

                # Save reviser comment
                if reviser_comment != "":
                    AaSrpRequestComment(
                        srp_request=srp_request,
                        comment=reviser_comment,
                        comment_type=AaSrpRequestComment.Type.REVISER_COMMENT,
                        creator=request.user,
                    ).save()

                srp_request.request_status = AaSrpRequest.Status.APPROVED
                srp_request.save()

                user_settings = AaSrpUserSettings.objects.get(user=request.user)

                # Check if the user has notifications activated (it's by default)
                if user_settings.disable_notifications is False:
                    ship_name = srp_request.ship.name
                    fleet_name = srp_request.srp_link.srp_name
                    srp_code = srp_request.srp_link.srp_code
                    request_code = srp_request.request_code
                    reviser = get_main_character_from_user(request.user)
                    reviser_comment = (
                        f"\nComment:\n{reviser_comment}\n"
                        if reviser_comment != ""
                        else ""
                    )
                    inquiry_note = SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE
                    notification_message = (
                        f"Your SRP request regarding your {ship_name} lost during "
                        f"{fleet_name} has been approved.\n\n"
                        f"Request Details:\nSRP-Code: {srp_code}\n"
                        f"Request-Code: {request_code}\n"
                        f"Reviser: {reviser}\n{reviser_comment}\n{inquiry_note}"
                    )

                    logger.info("Sending approval message to user")

                    send_user_notification(
                        user=requester,
                        level="success",
                        title="SRP Request Approved",
                        message=notification_message,
                    )

                data.append(
                    {"success": True, "message": _("SRP request has been approved")}
                )

    return JsonResponse(data, safe=False)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def ajax_srp_request_deny(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Ajax call :: Deny SRP request
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    data = []

    try:
        srp_request = AaSrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )
    except AaSrpRequest.DoesNotExist:
        data.append({"success": False})
    else:
        if request.method == "POST":
            # Create a form instance and populate it with data from the request
            form = AaSrpRequestRejectForm(request.POST)

            # Check whether it's valid:
            if form.is_valid():
                reject_info = form.cleaned_data["reject_info"]
                requester = srp_request.creator

                srp_request.payout_amount = 0
                srp_request.request_status = AaSrpRequest.Status.REJECTED
                srp_request.save()

                # Set new status in request history
                AaSrpRequestComment(
                    srp_request=srp_request,
                    comment_type=AaSrpRequestComment.Type.STATUS_CHANGE,
                    new_status=AaSrpRequest.Status.REJECTED,
                    creator=request.user,
                ).save()

                # Save reject reason as comment for this request
                AaSrpRequestComment(
                    comment=reject_info,
                    srp_request=srp_request,
                    comment_type=AaSrpRequestComment.Type.REJECT_REASON,
                    creator=request.user,
                ).save()

                user_settings = AaSrpUserSettings.objects.get(user=request.user)

                # Check if the user has notifications activated (it's by default)
                if user_settings.disable_notifications is False:
                    ship_name = srp_request.ship.name
                    fleet_name = srp_request.srp_link.srp_name
                    srp_code = srp_request.srp_link.srp_code
                    request_code = srp_request.request_code
                    reviser = get_main_character_from_user(request.user)
                    inquiry_note = SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE
                    notification_message = (
                        f"Your SRP request regarding your {ship_name} lost during "
                        f"{fleet_name} has been rejected.\n\n"
                        f"Reason:\n{reject_info}\n\n"
                        f"Request Details:\nSRP-Code: {srp_code}\n"
                        f"Request-Code: {request_code}\n"
                        f"Reviser: {reviser}\n\n{inquiry_note}"
                    )

                    logger.info("Sending reject message to user")

                    send_user_notification(
                        user=requester,
                        level="danger",
                        title=_("SRP Request Rejected"),
                        message=notification_message,
                    )

                data.append(
                    {"success": True, "message": _("SRP request has been rejected")}
                )

    return JsonResponse(data, safe=False)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def ajax_srp_request_remove(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Ajax call :: Remove SRP request
    :param request:
    :param srp_code:
    :param srp_request_code:
    """

    data = []

    try:
        srp_request = AaSrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )
    except AaSrpRequest.DoesNotExist:
        data.append({"success": False})
    else:
        srp_request.delete()

        data.append({"success": True, "message": _("SRP request has been removed")})

    return JsonResponse(data, safe=False)
