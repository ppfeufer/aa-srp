"""
General views

This module contains general views for the AA SRP application. These views handle
various functionalities such as rendering dashboards, managing SRP links, and
processing user requests.
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
from aasrp.models import Insurance, RequestComment, Setting, SrpLink, SrpRequest
from aasrp.providers import esi

# Initialize a logger with a custom tag for the AA SRP application
logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


@permission_required("aasrp.basic_access")
def srp_links(request: WSGIRequest, show_all_links: bool = False) -> HttpResponse:
    """
    Render the SRP dashboard view.

    This view displays the dashboard for Ship Replacement Program (SRP) links.
    It can show either all SRP links or only the available ones, depending on the
    `show_all_links` parameter and the user's permissions.

    :param request: The HTTP request object.
    :type request: WSGIRequest
    :param show_all_links: Flag to indicate whether to show all SRP links or only available ones. Defaults to False.
    :type show_all_links: bool
    :return: The rendered SRP dashboard view.
    :rtype: HttpResponse
    """

    logger_message = f"Dashboard with {'all' if show_all_links else 'available'} SRP links called by {request.user}"

    # Check if the user has the required permissions to view all SRP links
    if show_all_links and not request.user.has_perm("aasrp.manage_srp"):
        messages.error(
            request=request,
            message=_("You do not have the needed permissions to view all SRP links"),
        )

        return redirect(to="aasrp:srp_links")

    logger.info(msg=logger_message)

    # Prepare the context for rendering the dashboard
    context = {"show_all_links": show_all_links}

    return render(
        request=request, template_name="aasrp/dashboard.html", context=context
    )


@permission_required("aasrp.basic_access")
def view_own_requests(request: WSGIRequest) -> HttpResponse:
    """
    Render the view for a user's own SRP requests.

    This view displays a page where the user can see their own Ship Replacement Program (SRP) requests.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :return: The rendered HTML page displaying the user's SRP requests.
    :rtype: HttpResponse
    """

    logger.info(msg=f"Own SRP requests view called by {request.user}")

    return render(request=request, template_name="aasrp/view-own-requests.html")


@permission_required("aasrp.basic_access")
def user_settings(request: WSGIRequest) -> HttpResponse:
    """
    Render and handle the user settings form.

    This view allows users to view and update their settings. If the request method
    is POST, it processes the submitted form data and saves the changes. Otherwise,
    it displays the form with the current user settings.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :return: The rendered user settings page or a redirect after saving settings.
    :rtype: HttpResponse
    """

    # Retrieve the current settings for the logged-in user
    current_user_settings = get_user_settings(user=request.user)

    if request.method == "POST":
        # Populate the form with the submitted data and the current settings instance
        user_settings_form = UserSettingsForm(
            data=request.POST, instance=current_user_settings
        )

        # If the form is valid, save the data to the database
        if user_settings_form.is_valid():
            user_settings_form.save()

            # Display a success message to the user
            messages.success(request, _("Settings saved."))

            # Redirect the user back to the settings page
            return redirect("aasrp:user_settings")
    else:
        # Create a form instance pre-filled with the current user settings
        user_settings_form = UserSettingsForm(instance=current_user_settings)

    # Log the access to the user settings view
    logger.info(f"User settings view called by {request.user}")

    # Prepare the context for rendering the template
    context = {"user_settings_form": user_settings_form}

    # Render the user settings template with the provided context
    return render(request, "aasrp/user-settings.html", context)


@permissions_required(("aasrp.manage_srp", "aasrp.create_srp"))
def srp_link_add(request: WSGIRequest) -> HttpResponse:
    """
    Render and handle the form for adding a new SRP link.

    This view allows users to create a new Ship Replacement Program (SRP) link.
    If the request method is POST, it processes the submitted form data and saves
    the new SRP link. Otherwise, it displays a blank form for the user to fill out.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :return: The rendered form view or a redirect after creating the SRP link.
    :rtype: HttpResponse
    """

    request_user = request.user

    logger.info(msg=f"Add SRP link form called by {request_user}")

    # If this is a POST request, process the form data.
    if request.method == "POST":
        # Create a form instance and populate it with data from the request.
        form = SrpLinkForm(data=request.POST)

        # Check whether the form is valid.
        if form.is_valid():
            srp_name = form.cleaned_data["srp_name"]
            fleet_time = form.cleaned_data["fleet_time"]
            fleet_type = form.cleaned_data["fleet_type"]
            fleet_doctrine = form.cleaned_data["fleet_doctrine"]
            aar_link = form.cleaned_data["aar_link"]

            # Create and save the new SRP link.
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

            # Display a success message and redirect to the SRP links page.
            messages.success(
                request=request,
                message=_('SRP link "{srp_code}" created').format(
                    srp_code=srp_link.srp_code
                ),
            )

            return redirect(to="aasrp:srp_links")

    # If a GET (or any other method), create a blank form.
    else:
        form = SrpLinkForm()

    # Render the form template with the provided context.
    context = {"form": form}

    return render(request=request, template_name="aasrp/link-add.html", context=context)


@permissions_required(("aasrp.manage_srp", "aasrp.create_srp"))
def srp_link_edit(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    Render and handle the form for editing an SRP link.

    This view allows users to edit the After Action Report (AAR) link for a specific
    Ship Replacement Program (SRP) link identified by its `srp_code`. If the request
    method is POST, it processes the submitted form data and updates the SRP link.
    Otherwise, it displays the form pre-filled with the current SRP link data.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link to be edited.
    :type srp_code: str
    :return: The rendered form view or a redirect after updating the SRP link.
    :rtype: HttpResponse
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
            message=_("Unable to locate SRP link using SRP code {srp_code}").format(
                srp_code=srp_code
            ),
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
    ship_value: int,
    victim_id: int,
    additional_info: str,
) -> SrpRequest:
    """
    Save a Ship Replacement Program (SRP) request.

    This function creates and saves an SRP request based on the provided parameters.
    It also creates associated comments and insurance entries for the request.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_link: The SRP link associated with the request.
    :type srp_link: SrpLink
    :param killmail_link: The link to the killmail for the ship loss.
    :type killmail_link: str
    :param ship_type_id: The ID of the ship type involved in the loss.
    :type ship_type_id: int
    :param ship_value: The value of the lost ship.
    :type ship_value: int
    :param victim_id: The ID of the character who lost the ship.
    :type victim_id: int
    :param additional_info: Additional information provided for the SRP request.
    :type additional_info: str
    :return: The created SRP request object.
    :rtype: SrpRequest
    """

    # Retrieve the creator of the request and the current time
    creator = request.user
    post_time = timezone.now()

    # Get the character associated with the victim ID
    srp_request__character = EveCharacter.objects.get_character_by_id(
        character_id=victim_id
    )

    # Get ship information from ESI
    srp_request__ship = esi.client.Universe.GetUniverseTypesTypeId(
        type_id=ship_type_id
    ).result(force_refresh=True)

    logger.debug(msg=f"Ship type {srp_request__ship.name}")

    # Create the SRP request object
    srp_request = SrpRequest.objects.create(
        killboard_link=killmail_link,
        creator=creator,
        srp_link=srp_link,
        character=srp_request__character,
        ship_name=srp_request__ship.name,
        ship_id=ship_type_id,
        loss_amount=ship_value,
        post_time=post_time,
        request_code=get_random_string(length=16),
    )

    # Create comments for the SRP request
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

    # Retrieve insurance information for the ship type
    insurance_information = SrpRequest.objects.get_insurance_for_ship_type(
        ship_type_id=ship_type_id
    )

    # Create insurance entries for the SRP request
    Insurance.objects.bulk_create(
        [
            Insurance(
                srp_request=srp_request,
                insurance_level=level.name,
                insurance_cost=level.cost,
                insurance_payout=level.payout,
            )
            for level in insurance_information.levels
        ]
    )

    # Log the creation of the SRP request
    logger.info(
        msg=(
            f"Created SRP request on behalf of user {creator} "
            f"(character: {srp_request__character}) for fleet name {srp_link.srp_name} "
            f"with SRP code {srp_link.srp_code}"
        )
    )

    # Display a success message to the user
    messages.success(
        request=request,
        message=_("Submitted SRP request for your {ship_name}.").format(
            ship_name=srp_request__ship.name
        ),
    )

    return srp_request


@permission_required("aasrp.basic_access")
def request_srp(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    Handle the SRP request form.

    This view allows users to submit a Ship Replacement Program (SRP) request for a specific SRP link
    identified by its `srp_code`. It validates the SRP code, checks the SRP link status, processes the
    submitted form data, and saves the SRP request if valid. If the request method is GET, it displays
    a blank form.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link for which the request is being made.
    :type srp_code: str
    :return: The rendered SRP request form or a redirect after processing the request.
    :rtype: HttpResponse
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
            message=_(
                "Unable to locate SRP Fleet using SRP code {srp_code}"
            ).format(  # pylint: disable=consider-using-f-string
                srp_code=srp_code
            ),
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
            loss_value_field = Setting.objects.get_setting(
                Setting.Field.LOSS_VALUE_SOURCE
            )

            # Parse killmail
            try:
                srp_kill_link_id = SrpRequest.objects.get_kill_id(
                    killboard_link=submitted_killmail_link
                )
                ship_type_id, ship_value, victim_id = SrpRequest.objects.get_kill_data(
                    killmail_id=srp_kill_link_id, loss_value_field=loss_value_field
                )
            except ValueError as err:
                # Invalid killmail
                error_message_text = (
                    _(
                        "Something went wrong, your kill mail ({submitted_killmail_link}) could not be parsed: {error}"
                    ).format(  # pylint: disable=consider-using-f-string
                        submitted_killmail_link=submitted_killmail_link, error=str(err)
                    )
                    if str(err)
                    else (
                        "Your kill mail link ({submitted_killmail_link}) is invalid or "
                        "the zKillboard API is not answering at the moment. "
                        "Please make sure you are using either {zkillboard_base_url}, "
                        "{evekb_base_url} or {evekill_base_url}"
                    ).format(  # pylint: disable=consider-using-f-string
                        submitted_killmail_link=submitted_killmail_link,
                        zkillboard_base_url=KILLBOARD_DATA["zKillboard"]["base_url"],
                        evekb_base_url=KILLBOARD_DATA["EveTools"]["base_url"],
                        evekill_base_url=KILLBOARD_DATA["EVE-KILL"]["base_url"],
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
                    "Character {victim_id} does not belong to your Auth account. "
                    "Please add this character as an alt to your main and try again."
                ).format(victim_id=victim_id),
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
    Mark an SRP link as completed.

    This view updates the status of a specific Ship Replacement Program (SRP) link
    identified by its `srp_code` to "COMPLETED". If the SRP link does not exist,
    an error message is displayed.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link to be marked as completed.
    :type srp_code: str
    :return: A redirect to the SRP links page.
    :rtype: HttpResponse
    """

    logger.info(
        f"Complete SRP link form for SRP link {srp_code} called by {request.user}"
    )

    try:
        # Retrieve the SRP link using the provided code
        srp_link = SrpLink.objects.get(srp_code=srp_code)
        # Update the status of the SRP link to "COMPLETED"
        srp_link.srp_status = SrpLink.Status.COMPLETED
        srp_link.save()

        # Display a success message to the user
        messages.success(request, _("SRP link marked as completed"))
    except SrpLink.DoesNotExist:
        # Log an error and display an error message if the SRP link is not found
        logger.error(
            f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request,
            message=_("Unable to locate SRP link with ID {srp_code}").format(
                srp_code=srp_code
            ),
        )

    # Redirect the user to the SRP links page
    return redirect("aasrp:srp_links")


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_link_view_requests(request: WSGIRequest, srp_code: str) -> HttpResponse:
    """
    Render the view for SRP requests associated with a specific SRP link.

    This view retrieves and displays all Ship Replacement Program (SRP) requests
    for a given SRP link identified by its `srp_code`. If the SRP link does not exist,
    an error message is displayed, and the user is redirected to the SRP links page.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link for which requests are being viewed.
    :type srp_code: str
    :return: The rendered HTML page displaying the SRP requests or a redirect if the SRP link is not found.
    :rtype: HttpResponse
    """

    logger.info(f"View SRP requests for SRP link {srp_code} called by {request.user}")

    # Check if the provided SRP code is valid
    try:
        srp_link = SrpLink.objects.get(srp_code=srp_code)
    except SrpLink.DoesNotExist:
        logger.error(
            f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request,
            message=_("Unable to locate SRP link with ID {srp_code}").format(
                srp_code=srp_code
            ),
        )

        return redirect("aasrp:srp_links")

    # Prepare the context for rendering the view
    context = {
        "srp_link": srp_link,
        "forms": {
            "reject_request": SrpRequestRejectForm(),
            "accept_request": SrpRequestAcceptForm(),
            "accept_rejected_request": SrpRequestAcceptRejectedForm(),
        },
    }

    # Render the view with the provided context
    return render(request, "aasrp/view-requests.html", context)


@permission_required("aasrp.manage_srp")
def enable_srp_link(request: WSGIRequest, srp_code: str):
    """
    Enable an SRP link.

    This view sets the status of a specific Ship Replacement Program (SRP) link,
    identified by its `srp_code`, to "ACTIVE". If the SRP link does not exist,
    an error message is displayed.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link to be enabled.
    :type srp_code: str
    :return: A redirect to the SRP links page.
    :rtype: HttpResponse
    """

    logger.info(msg=f"Enable SRP link {srp_code} called by {request.user}")

    try:
        # Retrieve the SRP link using the provided code
        srp_link = SrpLink.objects.get(srp_code=srp_code)
        # Update the status of the SRP link to "ACTIVE"
        srp_link.srp_status = SrpLink.Status.ACTIVE
        srp_link.save()

        # Display a success message to the user
        messages.success(
            request=request,
            message=_("SRP link {srp_code} (re-)activated.").format(srp_code=srp_code),
        )
    except SrpLink.DoesNotExist:
        # Log an error and display an error message if the SRP link is not found
        logger.error(
            msg=f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request,
            message=_("Unable to locate SRP link with ID {srp_code}").format(
                srp_code=srp_code
            ),
        )

    # Redirect the user to the SRP links page
    return redirect(to="aasrp:srp_links")


@permission_required("aasrp.manage_srp")
def disable_srp_link(request: WSGIRequest, srp_code: str):
    """
    Disable an SRP link.

    This view sets the status of a specific Ship Replacement Program (SRP) link,
    identified by its `srp_code`, to "CLOSED". If the SRP link does not exist,
    an error message is displayed.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link to be disabled.
    :type srp_code: str
    :return: A redirect to the SRP links page.
    :rtype: HttpResponse
    """

    logger.info(msg=f"Disable SRP link {srp_code} called by {request.user}")

    try:
        # Retrieve the SRP link using the provided code
        srp_link = SrpLink.objects.get(srp_code=srp_code)
        # Update the status of the SRP link to "CLOSED"
        srp_link.srp_status = SrpLink.Status.CLOSED
        srp_link.save()

        # Display a success message to the user
        messages.success(
            request=request,
            message=_("SRP link {srp_code} disabled.").format(srp_code=srp_code),
        )
    except SrpLink.DoesNotExist:
        # Log an error and display an error message if the SRP link is not found
        logger.error(
            msg=f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request,
            message=_("Unable to locate SRP link with ID {srp_code}").format(
                srp_code=srp_code
            ),
        )

    # Redirect the user to the SRP links page
    return redirect(to="aasrp:srp_links")


@permission_required("aasrp.manage_srp")
def delete_srp_link(request: WSGIRequest, srp_code: str):
    """
    Delete an SRP link.

    This view handles the deletion of a specific Ship Replacement Program (SRP) link
    identified by its `srp_code`. If the SRP link does not exist, an error message is
    displayed. Upon successful deletion, a success message is shown.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link to be deleted.
    :type srp_code: str
    :return: A redirect to the SRP links page.
    :rtype: HttpResponse
    """

    logger.info(msg=f"Delete SRP link {srp_code} called by {request.user}")

    try:
        # Retrieve the SRP link using the provided code
        srp_link = SrpLink.objects.get(srp_code=srp_code)
        # Delete the SRP link
        srp_link.delete()

        # Display a success message to the user
        messages.success(
            request=request,
            message=_("SRP link {srp_code} deleted.").format(srp_code=srp_code),
        )
    except SrpLink.DoesNotExist:
        # Log an error and display an error message if the SRP link is not found
        logger.error(
            msg=f"Unable to locate SRP link using code {srp_code} for user {request.user}"
        )

        messages.error(
            request=request,
            message=_("Unable to locate SRP link with ID {srp_code}").format(
                srp_code=srp_code
            ),
        )

    # Redirect the user to the SRP links page
    return redirect(to="aasrp:srp_links")
