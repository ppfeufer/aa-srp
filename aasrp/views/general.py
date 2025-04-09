"""
General views
"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from eveuniverse.models import EveType

# AA SRP
from aasrp import __title__
from aasrp.constants import KILLBOARD_DATA
from aasrp.form import (
    SrpLinkForm,
    SrpLinkUpdateForm,
    SrpRequestAcceptForm,
    SrpRequestAcceptRejectedForm,
    SrpRequestForm,
    SrpRequestRejectForm,
    UserSettingsForm,
)
from aasrp.helper.notification import notify_srp_team
from aasrp.helper.user import get_user_settings
from aasrp.models import Insurance, RequestComment, SrpLink, SrpRequest

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


@permission_required("aasrp.basic_access")
def srp_links(request: WSGIRequest, show_all_links: bool = False) -> HttpResponse:
    """
    SRP dashboard

    :param request:
    :type request:
    :param show_all_links:
    :type show_all_links:
    :return:
    :rtype:
    """

    logger_message = f"Dashboard with {'all' if show_all_links else 'available'} SRP links called by {request.user}"

    if show_all_links and not request.user.has_perm("aasrp.manage_srp"):
        messages.error(
            request=request,
            message=_("You do not have the needed permissions to view all SRP links"),
        )

        return redirect(to="aasrp:srp_links")

    logger.info(msg=logger_message)

    context = {"show_all_links": show_all_links}

    return render(
        request=request, template_name="aasrp/dashboard.html", context=context
    )


@permission_required("aasrp.basic_access")
def view_own_requests(request: WSGIRequest) -> HttpResponse:
    """
    View own SRP requests

    :param request:
    :type request:
    :return:
    :rtype:
    """

    logger.info(msg=f"Own SRP requests view called by {request.user}")

    return render(request=request, template_name="aasrp/view-own-requests.html")


@permission_required("aasrp.basic_access")
def user_settings(request: WSGIRequest) -> HttpResponse:
    """
    User settings

    :param request:
    :type request:
    :return:
    :rtype:
    """

    current_user_settings = get_user_settings(user=request.user)

    if request.method == "POST":
        user_settings_form = UserSettingsForm(
            data=request.POST, instance=current_user_settings
        )

        # If the form is valid, save the data to the database.
        if user_settings_form.is_valid():
            user_settings_form.save()

            messages.success(request, _("Settings saved."))

            return redirect("aasrp:user_settings")
    else:
        user_settings_form = UserSettingsForm(instance=current_user_settings)

    logger.info(f"User settings view called by {request.user}")

    context = {"user_settings_form": user_settings_form}

    return render(request, "aasrp/user-settings.html", context)


@permissions_required(("aasrp.manage_srp", "aasrp.create_srp"))
def srp_link_add(request: WSGIRequest) -> HttpResponse:
    """
    Add a SRP link

    :param request:
    :type request:
    :return:
    :rtype:
    """

    request_user = request.user

    logger.info(msg=f"Add SRP link form called by {request_user}")

    # If this is a POST request, we need to process the form data.
    if request.method == "POST":
        # Create a form instance and populate it with data from the request.
        form = SrpLinkForm(data=request.POST)

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

            messages.success(
                request=request, message=_(f'SRP link "{srp_link.srp_code}" created')
            )

            return redirect(to="aasrp:srp_links")

    # If a GET (or any other method) we'll create a blank form.
    else:
        form = SrpLinkForm()

    context = {"form": form}

    return render(request=request, template_name="aasrp/link-add.html", context=context)


@permissions_required(("aasrp.manage_srp", "aasrp.create_srp"))
def srp_link_edit(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    Add or edit AAR link

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    request_user = request.user

    logger.info(f"Edit SRP link form for SRP code {srp_code} called by {request_user}")

    # Check if the provided SRP code is valid
    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
    except SrpLink.DoesNotExist:
        logger.error(
            msg=(
                f"Unable to locate SRP link using SRP code {srp_code} for "
                f"user {request_user}"
            )
        )

        messages.error(
            request=request,
            message=_(f"Unable to locate SRP link using SRP code {srp_code}"),
        )

        return redirect("aasrp:srp_links")

    # If this is a POST request, we need to process the form data.
    if request.method == "POST":
        form = SrpLinkUpdateForm(data=request.POST, instance=srp_link)

        if form.is_valid():
            srp_link.aar_link = form.cleaned_data["aar_link"]
            srp_link.save()

            messages.success(request, _("AAR link changed"))

            return redirect("aasrp:srp_links")
    else:
        form = SrpLinkUpdateForm(instance=srp_link)

    context = {"srp_code": srp_code, "form": form}

    return render(request, "aasrp/link-edit.html", context)


def _save_srp_request(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    request: WSGIRequest,
    srp_link: SrpLink,
    killmail_link: str,
    ship_type_id: int,
    ship_value: str,
    victim_id: int,
    additional_info: str,
) -> SrpRequest:
    """
    Saving the SRP request

    :param request:
    :type request:
    :param srp_link:
    :type srp_link:
    :param killmail_link:
    :type killmail_link:
    :param ship_type_id:
    :type ship_type_id:
    :param ship_value:
    :type ship_value:
    :param victim_id:
    :type victim_id:
    :param additional_info:
    :type additional_info:
    :return:
    :rtype:
    """

    creator = request.user
    post_time = timezone.now()
    srp_request__character = EveCharacter.objects.get_character_by_id(
        character_id=victim_id
    )

    (
        srp_request__ship,
        created_from_esi,  # pylint: disable=unused-variable
    ) = EveType.objects.get_or_create_esi(id=ship_type_id)

    srp_request = SrpRequest.objects.create(
        killboard_link=killmail_link,
        creator=creator,
        srp_link=srp_link,
        character=srp_request__character,
        ship_name=srp_request__ship.name,
        ship=srp_request__ship,
        loss_amount=ship_value,
        post_time=post_time,
        request_code=get_random_string(length=16),
    )

    RequestComment.objects.bulk_create(
        [
            RequestComment(
                srp_request=srp_request,
                comment_type=RequestComment.Type.REQUEST_ADDED,
                creator=creator,
                new_status=SrpRequest.Status.PENDING,
            ),
            RequestComment(
                comment=additional_info,
                srp_request=srp_request,
                comment_type=RequestComment.Type.REQUEST_INFO,
                creator=creator,
            ),
        ]
    )

    insurance_information = SrpRequest.objects.get_insurance_for_ship_type(
        ship_type_id=ship_type_id
    )
    Insurance.objects.bulk_create(
        [
            Insurance(
                srp_request=srp_request,
                insurance_level=level["name"],
                insurance_cost=level["cost"],
                insurance_payout=level["payout"],
            )
            for level in insurance_information["levels"]
        ]
    )

    logger.info(
        msg=(
            f"Created SRP request on behalf of user {creator} "
            f"(character: {srp_request__character}) for fleet name {srp_link.srp_name} "
            f"with SRP code {srp_link.srp_code}"
        )
    )

    messages.success(
        request=request,
        message=_(f"Submitted SRP request for your {srp_request__ship.name}."),
    )

    return srp_request


@permission_required("aasrp.basic_access")
def request_srp(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    SRP request

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    logger.info(
        msg=f"SRP request form for SRP code {srp_code} called by {request.user}"
    )

    # Check if the provided SRP code is valid
    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
    except SrpLink.DoesNotExist:
        logger.error(
            msg=(
                f"Unable to locate SRP Fleet using SRP code {srp_code} for "
                f"user {request.user}"
            )
        )

        messages.error(
            request=request,
            message=_(f"Unable to locate SRP Fleet using SRP code {srp_code}"),
        )

        return redirect("aasrp:srp_links")

    # Check if the SRP link is still open
    if srp_link.srp_status != SrpLink.Status.ACTIVE:
        messages.error(
            request=request,
            message=_("This SRP link is no longer available for SRP requests."),
        )

        return redirect(to="aasrp:srp_links")

    # If this is a POST request, we need to process the form data.
    if request.method == "POST":
        # Create a form instance and populate it with data from the request.
        form = SrpRequestForm(data=request.POST)

        logger.debug(msg=f"Request type POST contains valid form: {form.is_valid()}")

        if form.is_valid():
            submitted_killmail_link = form.cleaned_data["killboard_link"]
            srp_request_additional_info = form.cleaned_data["additional_info"]

            # Parse killmail
            try:
                srp_kill_link_id = SrpRequest.objects.get_kill_id(
                    killboard_link=submitted_killmail_link
                )
                ship_type_id, ship_value, victim_id = SrpRequest.objects.get_kill_data(
                    kill_id=srp_kill_link_id
                )
            except ValueError as err:
                # Invalid killmail
                error_message_text = (
                    (
                        "Something went wrong, your kill mail "
                        f"({submitted_killmail_link}) could not be parsed: {str(err)}"
                    )
                    if str(err)
                    else (
                        f"Your kill mail link ({submitted_killmail_link}) is invalid "
                        "or the zKillboard API is not answering at the moment. "
                        "Please make sure you are using either "
                        f"{KILLBOARD_DATA['zKillboard']['base_url']}, "
                        f"{KILLBOARD_DATA['EveTools']['base_url']} "
                        f"or {KILLBOARD_DATA['EVE-KILL']['base_url']}"
                    )
                )

                messages.error(request=request, message=error_message_text)

                return redirect(to="aasrp:srp_links")

            if request.user.character_ownerships.filter(
                character__character_id=str(victim_id)
            ).exists():
                # Save the SRP request
                srp_request = _save_srp_request(
                    request=request,
                    srp_link=srp_link,
                    killmail_link=submitted_killmail_link,
                    ship_type_id=ship_type_id,
                    ship_value=ship_value,
                    victim_id=victim_id,
                    additional_info=srp_request_additional_info,
                )

                # Send a message to the srp team in their discord channel.
                notify_srp_team(
                    srp_request=srp_request, additional_info=srp_request_additional_info
                )

                return redirect(to="aasrp:srp_links")

            messages.error(
                request=request,
                message=_(
                    f"Character {victim_id} does not belong to your Auth account. Please add this character as an alt to your main and try again."  # pylint: disable=line-too-long
                ),
            )

            return redirect(to="aasrp:srp_links")

    # If a GET (or any other method) we'll create a blank form.
    else:
        logger.debug(msg=f"Returning blank SRP request form for {request.user}")
        form = SrpRequestForm()

    context = {"srp_link": srp_link, "form": form}

    return render(
        request=request, template_name="aasrp/request-srp.html", context=context
    )


@permission_required("aasrp.manage_srp")
def complete_srp_link(request: WSGIRequest, srp_code: str):
    """
    Mark an SRP link as completed

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    logger.info(
        f"Complete SRP link form for SRP link {srp_code} called by {request.user}"
    )

    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
        srp_link.srp_status = SrpLink.Status.COMPLETED
        srp_link.save()

        messages.success(request, _("SRP link marked as completed"))
    except SrpLink.DoesNotExist:
        logger.error(
            f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP link with ID {srp_code}"))

    return redirect("aasrp:srp_links")


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_link_view_requests(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    View SRP requests for a specific SRP code

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    logger.info(f"View SRP requests for SRP link {srp_code} called by {request.user}")

    # Check if the provided SRP code is valid
    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
    except SrpLink.DoesNotExist:
        logger.error(
            f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(request, _(f"Unable to locate SRP link with ID {srp_code}"))

        return redirect("aasrp:srp_links")

    context = {
        "srp_link": srp_link,
        "forms": {
            "reject_request": SrpRequestRejectForm(),
            "accept_request": SrpRequestAcceptForm(),
            "accept_rejected_request": SrpRequestAcceptRejectedForm(),
        },
    }

    return render(request, "aasrp/view-requests.html", context)


@permission_required("aasrp.manage_srp")
def enable_srp_link(request: WSGIRequest, srp_code: str):
    """
    Enable SRP link

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    logger.info(msg=f"Enable SRP link {srp_code} called by {request.user}")

    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
        srp_link.srp_status = SrpLink.Status.ACTIVE
        srp_link.save()

        messages.success(
            request=request, message=_(f"SRP link {srp_code} (re-)activated.")
        )
    except SrpLink.DoesNotExist:
        logger.error(
            msg=f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP link with ID {srp_code}")
        )

    return redirect(to="aasrp:srp_links")


@permission_required("aasrp.manage_srp")
def disable_srp_link(request: WSGIRequest, srp_code: str):
    """
    Disable SRP link

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    logger.info(msg=f"Disable SRP link {srp_code} called by {request.user}")

    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
        srp_link.srp_status = SrpLink.Status.CLOSED
        srp_link.save()

        messages.success(request=request, message=_(f"SRP link {srp_code} disabled."))
    except SrpLink.DoesNotExist:
        logger.error(
            msg=f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP link with ID {srp_code}")
        )

    return redirect(to="aasrp:srp_links")


@permission_required("aasrp.manage_srp")
def delete_srp_link(request: WSGIRequest, srp_code: str):
    """
    Delete SRP link

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    logger.info(msg=f"Delete SRP link {srp_code} called by {request.user}")

    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
        srp_link.delete()

        messages.success(request=request, message=_(f"SRP link {srp_code} deleted."))
    except SrpLink.DoesNotExist:
        logger.error(
            msg=f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP link with ID {srp_code}")
        )

    return redirect(to="aasrp:srp_links")
