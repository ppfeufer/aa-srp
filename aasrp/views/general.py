"""
General views
"""

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
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
from aasrp.managers import SrpManager
from aasrp.models import Insurance, RequestComment, SrpLink, SrpRequest

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


@login_required
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

    logger_message = f"Dashboard with available SRP links called by {request.user}"

    if show_all_links is True:
        if not request.user.has_perm("aasrp.manage_srp"):
            messages.error(
                request=request,
                message=_(
                    "You do not have the needed permissions to view all SRP links"
                ),
            )

            return redirect(to="aasrp:srp_links")

        logger_message = f"Dashboard with all SRP links called by {request.user}"

    logger.info(msg=logger_message)

    context = {"show_all_links": show_all_links}

    return render(
        request=request, template_name="aasrp/dashboard.html", context=context
    )


@login_required
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


@login_required
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

    # If this is a POST request, we need to process the form data.
    if request.method == "POST":
        user_settings_form = UserSettingsForm(
            data=request.POST, instance=current_user_settings
        )

        # Check whether it's valid:
        if user_settings_form.is_valid():
            current_user_settings.disable_notifications = (
                user_settings_form.cleaned_data["disable_notifications"]
            )
            current_user_settings.save()

            messages.success(request=request, message=_("Settings saved."))

            return redirect(to="aasrp:user_settings")
    else:
        user_settings_form = UserSettingsForm(instance=current_user_settings)

    logger.info(msg=f"User settings view called by {request.user}")

    context = {"user_settings_form": user_settings_form}

    return render(
        request=request, template_name="aasrp/user-settings.html", context=context
    )


@login_required
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


@login_required
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
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            msg=f"Unable to locate SRP Fleet using code {srp_code} for user {request_user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP code with ID {srp_code}")
        )

        return redirect(to="aasrp:srp_links")

    srp_link = SrpLink.objects.get(srp_code=srp_code)

    # If this is a POST request, we need to process the form data.
    if request.method == "POST":
        # Create a form instance and populate it with data
        form = SrpLinkUpdateForm(data=request.POST, instance=srp_link)

        # Check whether it's valid:
        if form.is_valid():
            aar_link = form.cleaned_data["aar_link"]

            srp_link.aar_link = aar_link
            srp_link.save()

            messages.success(request=request, message=_("AAR link changed"))

            return redirect(to="aasrp:srp_links")
    else:
        form = SrpLinkUpdateForm(instance=srp_link)

    context = {"srp_code": srp_code, "form": form}

    return render(
        request=request, template_name="aasrp/link-edit.html", context=context
    )


def _save_srp_request(  # pylint: disable=too-many-arguments, too-many-locals, too-many-positional-arguments
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

    srp_request = SrpRequest(
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
    srp_request.save()

    # Save Request Create Even in request history
    RequestComment(
        srp_request=srp_request,
        comment_type=RequestComment.Type.REQUEST_ADDED,
        creator=creator,
        new_status=SrpRequest.Status.PENDING,
    ).save()

    # Add request info to request history
    RequestComment(
        comment=additional_info,
        srp_request=srp_request,
        comment_type=RequestComment.Type.REQUEST_INFO,
        creator=creator,
    ).save()

    # Add insurance information
    insurance_information = SrpManager.get_insurance_for_ship_type(
        ship_type_id=ship_type_id
    )

    for insurance_level in insurance_information["levels"]:
        logger.debug(msg=insurance_level)

        Insurance(
            srp_request=srp_request,
            insurance_level=insurance_level["name"],
            insurance_cost=insurance_level["cost"],
            insurance_payout=insurance_level["payout"],
        ).save()

    srp_name = srp_link.srp_name
    srp_code = srp_link.srp_code
    logger.info(
        msg=(
            f"Created SRP request on behalf of user {creator} "
            f"(character: {srp_request__character}) for fleet name {srp_name} "
            f"with SRP code {srp_code}"
        )
    )

    messages.success(
        request=request,
        message=_(f"Submitted SRP request for your {srp_request__ship.name}."),
    )

    return srp_request


@login_required
@permission_required("aasrp.basic_access")
def request_srp(  # pylint: disable=too-many-locals
    request: WSGIRequest, srp_code: str
) -> HttpResponse:
    """
    SRP request

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    request_user = request.user

    logger.info(
        msg=f"SRP request form for SRP code {srp_code} called by {request_user}"
    )

    # Check if the provided SRP code is valid
    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
    except SrpLink.DoesNotExist:
        logger.error(
            msg=(
                f"Unable to locate SRP Fleet using SRP code {srp_code} for "
                f"user {request_user}"
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
        form_is_valid = form.is_valid()

        logger.debug(msg=f"Request type POST contains valid form: {form_is_valid}")

        # Check whether it's valid:
        if form.is_valid():
            submitted_killmail_link = form.cleaned_data["killboard_link"]
            srp_request_additional_info = form.cleaned_data["additional_info"]

            # Parse killmail
            try:
                srp_kill_link_id = SrpManager.get_kill_id(
                    killboard_link=submitted_killmail_link
                )

                (ship_type_id, ship_value, victim_id) = SrpManager.get_kill_data(
                    kill_id=srp_kill_link_id
                )
            except ValueError as err:
                # Invalid killmail
                logger.debug(
                    msg=(
                        f"User {request_user} submitted an invalid killmail link "
                        f"({submitted_killmail_link}) or zKillboard server could "
                        "not be reached"
                    )
                )

                if len(str(err)) > 0:
                    error_message_text = _(
                        f"Something went wrong, your kill mail ({submitted_killmail_link}) could not be parsed: {str(err)}"  # pylint: disable=line-too-long
                    )
                else:
                    zkillboard_base_url: str = KILLBOARD_DATA["zKillboard"]["base_url"]
                    evetools_base_url: str = KILLBOARD_DATA["EveTools"]["base_url"]
                    eve_kill_base_url: str = KILLBOARD_DATA["EVE-KILL"]["base_url"]
                    error_message_text = _(
                        f"Your kill mail link ({submitted_killmail_link}) is invalid or the zKillboard API is not answering at the moment. Please make sure you are using either {zkillboard_base_url}, {evetools_base_url} or {eve_kill_base_url}"  # pylint: disable=line-too-long
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


@login_required
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
        msg=f"Complete SRP link form for SRP code {srp_code} called by {request.user}"
    )

    # check if the provided SRP code is valid
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            msg=f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP code with ID {srp_code}")
        )

        return redirect(to="aasrp:srp_links")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = SrpLink.Status.COMPLETED
    srp_link.save()

    messages.success(request=request, message=_("SRP link marked as completed"))

    return redirect(to="aasrp:srp_links")


@login_required
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

    logger.info(
        msg=f"View SRP request for SRP code {srp_code} called by {request.user}"
    )

    # Check if the provided SRP code is valid
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            msg=f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP code with ID {srp_code}")
        )

        return redirect(to="aasrp:srp_links")

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

    return render(
        request=request, template_name="aasrp/view-requests.html", context=context
    )


@login_required
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

    # Check if the provided SRP code is valid
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            msg=f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP code with ID {srp_code}")
        )

        return redirect(to="aasrp:srp_links")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = SrpLink.Status.ACTIVE
    srp_link.save()

    messages.success(request=request, message=_(f"SRP link {srp_code} (re-)activated."))

    return redirect(to="aasrp:srp_links")


@login_required
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

    # Check if the provided SRP code is valid
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            msg=f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP code with ID {srp_code}")
        )

        return redirect(to="aasrp:srp_links")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    srp_link.srp_status = SrpLink.Status.CLOSED
    srp_link.save()

    messages.success(request=request, message=_(f"SRP link {srp_code} disabled."))

    return redirect(to="aasrp:srp_links")


@login_required
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

    # check if the provided SRP code is valid
    if SrpLink.objects.filter(srp_code=srp_code).exists() is False:
        logger.error(
            msg=f"Unable to locate SRP Fleet using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request, message=_(f"Unable to locate SRP code with ID {srp_code}")
        )

        return redirect(to="aasrp:srp_links")

    srp_link = SrpLink.objects.get(srp_code=srp_code)
    srp_link.delete()

    messages.success(request=request, message=_(f"SRP link {srp_code} deleted."))

    return redirect(to="aasrp:srp_links")
