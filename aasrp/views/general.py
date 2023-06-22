"""
General views
"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
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
from app_utils.urls import site_absolute_url
from eveuniverse.models import EveType

# AA SRP
from aasrp import __title__
from aasrp.constants import ZKILLBOARD_BASE_URL
from aasrp.form import (
    SrpLinkForm,
    SrpLinkUpdateForm,
    SrpRequestAcceptForm,
    SrpRequestAcceptRejectedForm,
    SrpRequestForm,
    SrpRequestRejectForm,
    UserSettingsForm,
)
from aasrp.helper.notification import send_message_to_discord_channel
from aasrp.helper.user import get_user_settings
from aasrp.managers import SrpManager
from aasrp.models import Insurance, RequestComment, Setting, SrpLink, SrpRequest

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


@login_required
@permission_required("aasrp.basic_access")
def dashboard(request: WSGIRequest, show_all_links: bool = False) -> HttpResponse:
    """
    SRP dashboard
    :param request:
    :param show_all_links:
    :return:
    """

    user_settings = get_user_settings(user=request.user)

    # If this is a POST request, we need to process the form data
    if request.method == "POST":
        user_settings_form = UserSettingsForm(request.POST, instance=user_settings)

        # Check whether it's valid:
        if user_settings_form.is_valid():
            user_settings.disable_notifications = user_settings_form.cleaned_data[
                "disable_notifications"
            ]
            user_settings.save()

            messages.success(request, _("Settings saved."))

            return redirect("aasrp:dashboard")
    else:
        user_settings_form = UserSettingsForm(instance=user_settings)

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
@permissions_required(("aasrp.manage_srp", "aasrp.create_srp"))
def srp_link_add(request: WSGIRequest) -> HttpResponse:
    """
    Add a SRP link
    :param request:
    :return:
    """

    logger.info("Add SRP link form called by %s", request.user)

    # If this is a POST request, we need to process the form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = SrpLinkForm(request.POST)

        # Check whether it's valid:
        if form.is_valid():
            srp_name = form.cleaned_data["srp_name"]
            fleet_time = form.cleaned_data["fleet_time"]
            fleet_type = form.cleaned_data["fleet_type"]
            fleet_doctrine = form.cleaned_data["fleet_doctrine"]
            aar_link = form.cleaned_data["aar_link"]

            srp_link = SrpLink(
                srp_name=srp_name,
                fleet_time=fleet_time,
                fleet_type=fleet_type,
                fleet_doctrine=fleet_doctrine,
                aar_link=aar_link,
                srp_code=get_random_string(length=16),
                fleet_commander=request.user.profile.main_character,
                creator=request.user,
            )
            srp_link.save()

            messages.success(request, _(f'SRP link "{srp_link.srp_code}" created'))

            return redirect("aasrp:dashboard")

    # If a GET (or any other method) we'll create a blank form
    else:
        form = SrpLinkForm()

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
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request_user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = SrpLink.objects.get(srp_code=srp_code)

    # If this is a POST request, we need to process the form data
    if request.method == "POST":
        # Create a form instance and populate it with data
        form = SrpLinkUpdateForm(request.POST, instance=srp_link)

        # Check whether it's valid:
        if form.is_valid():
            aar_link = form.cleaned_data["aar_link"]

            srp_link.aar_link = aar_link
            srp_link.save()

            messages.success(request, _("AAR link changed"))

            return redirect("aasrp:dashboard")
    else:
        form = SrpLinkUpdateForm(instance=srp_link)

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
    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
    except SrpLink.DoesNotExist:
        logger.error(
            f"Unable to locate SRP Fleet using SRP code {srp_code} for "
            f"user {request_user}"
        )

        messages.error(
            request, _(f"Unable to locate SRP Fleet using SRP code {srp_code}")
        )

        return redirect("aasrp:dashboard")

    # Check if the SRP link is still open
    if srp_link.srp_status != SrpLink.Status.ACTIVE:
        messages.error(
            request, _("This SRP link is no longer available for SRP requests.")
        )

        return redirect("aasrp:dashboard")

    # If this is a POST request, we need to process the form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = SrpRequestForm(request.POST)
        form_is_valid = form.is_valid()

        logger.debug(f"Request type POST contains valid form: {form_is_valid}")

        # Check whether it's valid:
        if form.is_valid():
            creator = request.user
            post_time = timezone.now()
            submitted_killmail_link = form.cleaned_data["killboard_link"]

            # Parse killmail
            try:
                srp_kill_link = SrpManager.get_kill_id(submitted_killmail_link)

                (ship_type_id, ship_value, victim_id) = SrpManager.get_kill_data(
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
                        f"Your SRP request Killmail link is invalid. Please make sure you are using {ZKILLBOARD_BASE_URL}"  # pylint: disable=line-too-long
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

                srp_request = SrpRequest(
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
                RequestComment(
                    srp_request=srp_request,
                    comment_type=RequestComment.Type.REQUEST_ADDED,
                    creator=creator,
                    new_status=SrpRequest.Status.PENDING,
                ).save()

                # Add request info to request history
                srp_request_additional_info = form.cleaned_data["additional_info"]
                RequestComment(
                    comment=srp_request_additional_info,
                    srp_request=srp_request,
                    comment_type=RequestComment.Type.REQUEST_INFO,
                    creator=creator,
                ).save()

                # Add insurance information
                insurance_information = SrpManager.get_insurance_for_ship_type(
                    ship_type_id=ship_type_id
                )

                for insurance_level in insurance_information["levels"]:
                    logger.debug(insurance_level)

                    insurance = Insurance(
                        srp_request=srp_request,
                        insurance_level=insurance_level["name"],
                        insurance_cost=insurance_level["cost"],
                        insurance_payout=insurance_level["payout"],
                    )
                    insurance.save()

                user_name = request.user
                character_name = srp_request__character
                srp_name = srp_link.srp_name
                srp_code = srp_link.srp_code
                logger.info(
                    f"Created SRP request on behalf of user {user_name} "
                    f"(character: {character_name}) for fleet name {srp_name} "
                    f"with SRP code {srp_code}"
                )

                ship = srp_request.ship.name
                messages.success(request, _(f"Submitted SRP request for your {ship}."))

                # Send a message to the srp team in their discord channel
                srp_team_discord_channel = Setting.objects.get_setting(
                    Setting.Field.SRP_TEAM_DISCORD_CHANNEL_ID
                )
                if srp_team_discord_channel is not None:
                    site_base_url = site_absolute_url()
                    request_code = srp_request.request_code
                    character_name = srp_request__character.character_name
                    ship_type = srp_request__ship.name
                    zkillboard_link = srp_request.killboard_link
                    additional_information = srp_request_additional_info.replace(
                        "@", "{@}"
                    )
                    srp_link = site_base_url + reverse(
                        "aasrp:view_srp_requests", args=[srp_code]
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
                        "Sending SRP request notification to the SRP team channel "
                        "on Discord"
                    )

                    send_message_to_discord_channel(
                        channel_id=srp_team_discord_channel,
                        title=title,
                        message=message,
                    )

                return redirect("aasrp:dashboard")

            messages.error(
                request,
                _(
                    f"Character {victim_id} does not belong to your Auth account. Please add this character as an alt to your main and try again."  # pylint: disable=line-too-long
                ),
            )

            return redirect("aasrp:dashboard")

    # If a GET (or any other method) we'll create a blank form
    else:
        logger.debug(f"Returning blank SRP request form for {request.user}")

        form = SrpRequestForm()

    context = {"srp_link": srp_link, "form": form}

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
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = SrpLink.Status.COMPLETED
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
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    reject_form = SrpRequestRejectForm()
    accept_form = SrpRequestAcceptForm()
    accept_rejected_form = SrpRequestAcceptRejectedForm()

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
@permission_required("aasrp.manage_srp")
def enable_srp_link(request: WSGIRequest, srp_code: str):
    """
    Enable SRP link
    :param request:
    :param srp_code:
    """

    logger.info(f"Enable SRP link {srp_code} called by {request.user}")

    # Check if the provided SRP code is valid
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = SrpLink.Status.ACTIVE
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
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = SrpLink.Status.CLOSED
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
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP code with ID {srp_code}"))

        return redirect("aasrp:dashboard")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    srp_link.delete()

    messages.success(request, _(f"SRP link {srp_code} deleted."))

    return redirect("aasrp:dashboard")
