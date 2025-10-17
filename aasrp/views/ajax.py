"""
Ajax views

This module contains views that handle AJAX requests for the AA SRP application.
These views are responsible for processing data asynchronously and returning
JSON responses or rendering partial templates as needed.
"""

# Standard Library
import json

# Django
from django.contrib.auth.decorators import permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.framework.api.user import get_main_character_name_from_user
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import reverse_absolute

# AA SRP
from aasrp import __title__
from aasrp.form import (
    SrpRequestAcceptForm,
    SrpRequestAcceptRejectedForm,
    SrpRequestPayoutForm,
    SrpRequestRejectForm,
)
from aasrp.helper.character import get_formatted_character_name
from aasrp.helper.eve_images import get_type_render_url_from_type_id
from aasrp.helper.icons import (
    copy_to_clipboard_icon,
    dashboard_action_icons,
    get_srp_request_action_icons,
    get_srp_request_details_icon,
    get_srp_request_status_icon,
)
from aasrp.helper.notification import notify_requester
from aasrp.helper.srp_data import (
    payout_amount_html,
    request_code_html,
    request_fleet_details_html,
)
from aasrp.helper.user import get_user_settings
from aasrp.models import RequestComment, SrpLink, SrpRequest

# Initialize a logger with a custom tag for the AA SRP application
logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


@permission_required("aasrp.basic_access")
def dashboard_srp_links_data(
    request: WSGIRequest, show_all_links: bool = False
) -> JsonResponse:
    """
    Handle an AJAX request to retrieve all active Ship Replacement Program (SRP) links.

    This view generates a JSON response containing data about SRP links, including
    their name, creator, fleet details, costs, status, and associated actions. If
    `show_all_links` is set to `True`, all SRP links are included; otherwise, only
    active links are returned.

    :param request: The HTTP request object.
    :type request: WSGIRequest
    :param show_all_links: A flag indicating whether to include all SRP links or only active ones.
    :type show_all_links: bool
    :return: A JSON response containing SRP link data.
    :rtype: JsonResponse
    """

    data = []

    # Retrieve all SRP links with related data preloaded for efficiency
    srp_links = SrpLink.objects.prefetch_related(
        "fleet_commander",
        "creator",
        "creator__profile__main_character",
        "srp_requests",
    ).all()

    # Filter to include only active SRP links if `show_all_links` is False
    if not show_all_links:
        srp_links = srp_links.filter(srp_status=SrpLink.Status.ACTIVE)

    # Iterate through each SRP link and prepare its data for the response
    for srp_link in srp_links:
        # Generate a localized "Link" text and create an AAR link if available
        l10n_link = _("Link")
        aar_link = (
            f'<a href="{srp_link.aar_link}" target="_blank">{l10n_link}</a>'
            if srp_link.aar_link
            else ""
        )

        # Prepare the SRP code with a copy-to-clipboard icon if the link is active
        srp_code_html = srp_link.srp_code
        if srp_link.srp_status == SrpLink.Status.ACTIVE:
            srp_link_href = reverse_absolute(
                viewname="aasrp:request_srp", args=[srp_link.srp_code]
            )
            title = _("Copy SRP link to clipboard")
            copy_icon = copy_to_clipboard_icon(data=srp_link_href, title=title)
            srp_code_html += f"<sup>{copy_icon}</sup>"

        # Retrieve the fleet type name if available
        fleet_type = srp_link.fleet_type.name if srp_link.fleet_type else ""

        # Append the SRP link data to the response list
        data.append(
            {
                "srp_name": srp_link.srp_name,
                "creator": get_main_character_name_from_user(user=srp_link.creator),
                "fleet_time": srp_link.fleet_time,
                "fleet_type": fleet_type,
                "fleet_doctrine": srp_link.fleet_doctrine,
                "aar_link": aar_link,
                "srp_code": {"display": srp_code_html, "sort": srp_link.srp_code},
                "srp_costs": srp_link.total_cost,
                "srp_status": srp_link.srp_status,
                "pending_requests": srp_link.pending_requests,
                "actions": dashboard_action_icons(request=request, srp_link=srp_link),
            }
        )

    # Return the prepared data as a JSON response
    return JsonResponse(data=data, safe=False)


@permission_required("aasrp.basic_access")
def dashboard_user_srp_requests_data(request: WSGIRequest) -> JsonResponse:
    """
    Handle an AJAX request to retrieve all SRP (Ship Replacement Program) requests made by the current user.

    This view generates a JSON response containing data about the user's SRP requests, including details
    about the ship, fleet, payout, and request status. The data is formatted for use in a dashboard or
    datatable.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :return: A JSON response containing the user's SRP request data.
    :rtype: JsonResponse
    """

    data = []

    # Retrieve all SRP requests created by the current user, prefetching related data for efficiency
    requests = (
        SrpRequest.objects.filter(creator=request.user)
        # .filter(ship__isnull=False)  # Uncomment to filter out requests without a ship
        .prefetch_related(
            "creator",
            "creator__profile__main_character",
            "character",
            "srp_link",
            "srp_link__creator",
            "srp_link__creator__profile__main_character",
        )
    )

    # Iterate through each SRP request and prepare its data for the response
    for srp_request in requests:
        killboard_link = ""

        # Generate a killboard link with the ship's render icon if available
        if srp_request.killboard_link:
            ship_render_icon_html = get_type_render_url_from_type_id(
                evetype_id=srp_request.ship_id,
                evetype_name=srp_request.ship_name,
                size=32,
                as_html=True,
            )

            zkb_link = srp_request.killboard_link
            zkb_link_text = srp_request.ship_name
            killboard_link = (
                f'<a href="{zkb_link}" target="_blank">'
                f"{ship_render_icon_html}"
                f"<span>{zkb_link_text}</span>"
                "</a>"
            )

        # Generate icons for the request status and details
        srp_request_status_icon = get_srp_request_status_icon(
            request=request, srp_request=srp_request
        )
        srp_request_details_icon = get_srp_request_details_icon(
            request=request, srp_link=srp_request.srp_link, srp_request=srp_request
        )

        # Format the character name for display and sorting
        character_display = get_formatted_character_name(
            character=srp_request.character, with_portrait=True
        )
        character_sort = get_formatted_character_name(character=srp_request.character)

        # Append the SRP request data to the response list
        data.append(
            {
                "request_time": srp_request.post_time,  # Time the request was posted
                "character": srp_request.character.character_name,  # Character name
                "character_html": {
                    "display": character_display,  # Formatted character name with portrait
                    "sort": character_sort,  # Character name for sorting
                },
                "fleet_name_html": {
                    "display": request_fleet_details_html(  # Fleet details
                        srp_request=srp_request
                    ),
                    "sort": srp_request.srp_link.srp_name,  # Fleet name for sorting
                },
                "srp_code": srp_request.srp_link.srp_code,  # SRP link code
                "request_code": srp_request.request_code,  # Unique request code
                "ship": srp_request.ship_name,  # Name of the ship
                "ship_html": {
                    "display": killboard_link,  # Killboard link with ship render icon
                    "sort": srp_request.ship_name,  # Ship name for sorting
                },
                "zkb_link": killboard_link,
                "zkb_loss_amount": srp_request.loss_amount,
                "payout_amount": srp_request.payout_amount,
                # "payout_amount_html": {
                #     "display": localized_isk_value(srp_request.payout_amount),
                #     "sort": srp_request.loss_amount,
                # },
                "request_status_icon": (
                    srp_request_details_icon + srp_request_status_icon
                ),  # Combined status and details icons
                "request_status": srp_request.get_request_status_display(),  # Translated request status
            }
        )

    # Return the prepared data as a JSON response
    return JsonResponse(data=data, safe=False)


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_link_view_requests_data(request: WSGIRequest, srp_code: str) -> JsonResponse:
    """
    Handle an AJAX request to retrieve data for all SRP (Ship Replacement Program) requests associated with a specific SRP link.

    This view generates a JSON response containing details about SRP requests, including the requester, ship, payout, and status.
    The data is formatted for use in a datatable or dashboard.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link.
    :type srp_code: str
    :return: A JSON response containing the SRP request data.
    :rtype: JsonResponse
    """

    data = []

    # Retrieve all SRP requests associated with the given SRP code, prefetching related data for efficiency
    srp_requests = SrpRequest.objects.filter(
        srp_link__srp_code__iexact=srp_code
    ).prefetch_related(
        "srp_link",
        "srp_link__creator",
        "srp_link__creator__profile__main_character",
        "character",
    )

    # Iterate through each SRP request and prepare its data for the response
    for srp_request in srp_requests:
        killboard_link = ""

        # Generate a killboard link with the ship's render icon if available
        if srp_request.killboard_link:
            ship_render_icon_html = get_type_render_url_from_type_id(
                evetype_id=srp_request.ship_id,
                evetype_name=srp_request.ship_name,
                size=32,
                as_html=True,
            )

            killboard_link = (
                f'<a href="{srp_request.killboard_link}" target="_blank">'
                f"{ship_render_icon_html}"
                f"<span>{srp_request.ship_name}</span></a>"
            )

        # Append the SRP request data to the response list
        data.append(
            {
                "request_time": srp_request.post_time,  # Time the request was posted
                "requester": get_main_character_name_from_user(
                    srp_request.creator
                ),  # Requester's main character name
                "character_html": {
                    "display": get_formatted_character_name(
                        character=srp_request.character,
                        with_portrait=True,
                        with_copy_icon=True,
                    ),  # Formatted character name with portrait and copy icon
                    "sort": srp_request.character.character_name,  # Character name for sorting
                },
                "character": srp_request.character.character_name,  # Character name
                "request_code_html": {
                    "display": request_code_html(
                        request_code=srp_request.request_code
                    ),  # HTML for request code
                    "sort": srp_request.request_code,  # Request code for sorting
                },
                "request_code": srp_request.request_code,
                "srp_code": srp_request.srp_link.srp_code,
                "ship_html": {"display": killboard_link, "sort": srp_request.ship_name},
                "ship": srp_request.ship_name,
                "zkb_link": killboard_link,
                "zbk_loss_amount": srp_request.loss_amount,
                "payout_amount_html": {
                    "display": payout_amount_html(
                        payout_amount=srp_request.payout_amount
                    ),  # Localized payout amount
                    "sort": srp_request.payout_amount,  # Payout amount for sorting
                },
                "payout_amount": srp_request.payout_amount,  # Payout amount
                "request_status_icon": get_srp_request_status_icon(
                    request=request, srp_request=srp_request
                ),  # Icon representing the request status
                "actions": get_srp_request_action_icons(
                    request=request,
                    srp_link=srp_request.srp_link,
                    srp_request=srp_request,
                ),  # Available actions for the request
                "request_status_translated": srp_request.get_request_status_display(),  # Translated request status
                "request_status": srp_request.request_status,  # Request status
            }
        )

    # Return the prepared data as a JSON response
    return JsonResponse(data=data, safe=False)


@permission_required("aasrp.basic_access")
def srp_request_additional_information(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> HttpResponse:
    """
    Handle an AJAX request to retrieve additional information for a specific SRP (Ship Replacement Program) request.

    This view fetches detailed information about an SRP request, including the ship type, requester details,
    insurance information, and request history. The data is rendered into an HTML template for display.

    :param request: The HTTP request object.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link.
    :type srp_code: str
    :param srp_request_code: The unique code identifying the SRP request.
    :type srp_request_code: str
    :return: An HTTP response containing the rendered HTML template with the SRP request details.
    :rtype: HttpResponse
    """

    # Retrieve the SRP request based on the provided SRP code and request code
    try:
        srp_request = SrpRequest.objects.get(
            srp_link__srp_code=srp_code, request_code=srp_request_code
        )
    except SrpRequest.DoesNotExist:
        return HttpResponseNotFound("SRP request not found")

    # Fetch insurance information related to the SRP request
    insurance_information = srp_request.insurance.filter(srp_request=srp_request)

    # Format the character name with a portrait for display
    character = get_formatted_character_name(
        character=srp_request.character, with_portrait=True, portrait_size=64
    )

    # Generate the ship render icon HTML for the SRP request
    ship_render_icon_html = get_type_render_url_from_type_id(
        evetype_id=srp_request.ship_id,
        evetype_name=srp_request.ship_name,
        size=64,
        as_html=True,
    )

    # Determine the alert level for the request status banner
    request_status_banner_alert_level = {
        SrpRequest.Status.APPROVED: "success",
        SrpRequest.Status.REJECTED: "danger",
    }.get(srp_request.request_status, "info")

    # Retrieve additional information comments for the SRP request
    additional_info = RequestComment.objects.filter(
        srp_request=srp_request, comment_type=RequestComment.Type.REQUEST_INFO
    ).first()
    additional_info = additional_info.comment if additional_info else ""

    # Retrieve the history of comments for the SRP request
    request_history = RequestComment.objects.filter(
        ~Q(comment_type=RequestComment.Type.REQUEST_INFO),
        srp_request=srp_request,
    ).order_by("pk")

    # Prepare the data to be passed to the template
    data = {
        "srp_request": srp_request,
        "ship_render_icon_html": ship_render_icon_html,
        "ship_type": srp_request.ship_name,
        "requester": get_main_character_name_from_user(user=srp_request.creator),
        "character": character,
        "additional_info": additional_info,
        "request_status_banner_alert_level": request_status_banner_alert_level,
        "request_status": srp_request.get_request_status_display(),
        "insurance_information": insurance_information,
        "request_history": request_history,
    }

    # Render the data into the specified HTML template and return the response
    return render(
        request=request,
        template_name="aasrp/ajax-render/srp-request-additional-information.html",
        context=data,
    )


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_request_change_payout(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Handle an AJAX request to change the payout amount for a specific SRP (Ship Replacement Program) request.

    This view processes a POST request containing the new payout value for an SRP request identified by its
    unique SRP code and request code. If the request is valid, the payout amount is updated in the database.

    :param request: The HTTP request object containing metadata and POST data.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link.
    :type srp_code: str
    :param srp_request_code: The unique code identifying the SRP request.
    :type srp_request_code: str
    :return: A JSON response indicating whether the operation was successful.
    :rtype: JsonResponse
    """

    if request.method == "POST":
        try:
            # Retrieve the SRP request based on the provided SRP code and request code
            srp_request = SrpRequest.objects.get(
                request_code=srp_request_code, srp_link__srp_code=srp_code
            )
            # Initialize the form with the POST data
            form = SrpRequestPayoutForm(data=request.POST)

            # If the form is valid, update the payout amount and save the SRP request
            if form.is_valid():
                srp_request.payout_amount = form.cleaned_data["value"]
                srp_request.save()

                # Return a success response
                return JsonResponse(data={"success": True}, safe=False)
        except SrpRequest.DoesNotExist:
            # If the SRP request does not exist, handle the exception silently
            pass

    # Return a failure response if the request method is not POST or an error occurs
    return JsonResponse(data={"success": False}, safe=False)


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_request_approve(  # pylint: disable=too-many-locals
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Handle an AJAX request to approve a specific SRP (Ship Replacement Program) request.

    This view processes a POST request to approve an SRP request identified by its unique SRP code and request code.
    It validates the request, updates the request status, creates comments, and sends notifications to the requester.

    :param request: The HTTP request object containing metadata and POST data.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link.
    :type srp_code: str
    :param srp_request_code: The unique code identifying the SRP request.
    :type srp_request_code: str
    :return: A JSON response indicating whether the operation was successful.
    :rtype: JsonResponse
    """

    try:
        # Retrieve the SRP request based on the provided SRP code and request code
        srp_request = SrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )
    except SrpRequest.DoesNotExist:
        # Return an error response if the SRP request does not exist
        return JsonResponse(
            data={"success": False, "message": _("No matching SRP request found")},
            safe=False,
        )

    if request.method == "POST":
        # Determine the appropriate form based on the current request status
        form = (
            SrpRequestAcceptForm(data=json.loads(request.body))
            if srp_request.request_status == SrpRequest.Status.PENDING
            else (
                SrpRequestAcceptRejectedForm(data=json.loads(request.body))
                if srp_request.request_status == SrpRequest.Status.REJECTED
                else None
            )
        )

        # Validate the form data
        if not form.is_valid():
            return JsonResponse(
                data={"success": False, "message": _("Invalid form data")}, safe=False
            )

        requester = srp_request.creator
        # Set the payout amount to the loss amount if not already set
        srp_request.payout_amount = srp_request.payout_amount or srp_request.loss_amount

        # Create comments for the status change
        comments = [
            RequestComment(
                srp_request=srp_request,
                comment_type=RequestComment.Type.STATUS_CHANGE,
                new_status=SrpRequest.Status.APPROVED,
                creator=request.user,
            )
        ]

        # Add a reviser comment if provided
        reviser_comment = form.cleaned_data["comment"]

        if reviser_comment:
            comments.append(
                RequestComment(
                    srp_request=srp_request,
                    comment=reviser_comment,
                    comment_type=RequestComment.Type.REVISER_COMMENT,
                    creator=request.user,
                )
            )
        # Save the comments in bulk
        RequestComment.objects.bulk_create(comments)

        # Update the request status to approved and save the request
        srp_request.request_status = SrpRequest.Status.APPROVED
        srp_request.save()

        # Send a notification to the requester if notifications are enabled
        if not get_user_settings(user=requester).disable_notifications:
            logger.info(msg="Sending approval message to user")

            notify_requester(
                requester=requester,
                reviser=request.user,
                srp_request=srp_request,
                comment=reviser_comment,
            )

        # Return a success response
        return JsonResponse(
            data={"success": True, "message": _("SRP request has been approved")},
            safe=False,
        )

    # Return an error response if the request method is not POST
    return JsonResponse(
        data={"success": False, "message": _("Invalid request method")},
        safe=False,
    )


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_requests_bulk_approve(request: WSGIRequest, srp_code: str) -> JsonResponse:
    """
    Handle an AJAX request to approve multiple SRP (Ship Replacement Program) requests.

    This view processes a POST request containing a list of SRP request codes to approve. It validates the input,
    updates the status and payout amounts for the specified requests, creates comments for the status changes,
    and sends notifications to the requesters.

    :param request: The HTTP request object containing metadata and POST data.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link.
    :type srp_code: str
    :return: A JSON response indicating whether the operation was successful.
    :rtype: JsonResponse
    """

    if request.method == "POST":
        # Parse the request body to retrieve the list of SRP request codes
        request_body = json.loads(request.body)
        srp_request_codes = request_body.get("srp_request_codes")

        logger.debug(
            "Bulk approving SRP requests for code: %s, with request codes: %s",
            srp_code,
            srp_request_codes,
        )

        # Validate the input data
        if not srp_request_codes or not srp_code:
            return JsonResponse(
                data={"success": False, "message": _("Invalid form data")}, safe=False
            )

        # Retrieve the SRP requests that match the given codes and are pending approval
        srp_requests = SrpRequest.objects.filter(
            Q(request_code__in=srp_request_codes)
            & Q(srp_link__srp_code=srp_code)
            & Q(request_status=SrpRequest.Status.PENDING)
        )

        logger.debug(
            "Found %d SRP requests to approve for code: %s",
            srp_requests.count(),
            srp_code,
        )

        # If no matching requests are found, return an error response
        if not srp_requests.exists():
            return JsonResponse(
                data={"success": False, "message": _("No matching SRP requests found")},
                safe=False,
            )

        # Prepare the SRP requests for bulk update
        srp_request_list = list(srp_requests)
        for srp_request in srp_request_list:
            srp_request.payout_amount = (
                srp_request.payout_amount or srp_request.loss_amount
            )
            srp_request.request_status = SrpRequest.Status.APPROVED

        # Perform a bulk update of the SRP requests
        SrpRequest.objects.bulk_update(
            srp_request_list, ["payout_amount", "request_status"]
        )

        # Create comments for the status changes in bulk
        comments = [
            RequestComment(
                srp_request=srp_request,
                comment_type=RequestComment.Type.STATUS_CHANGE,
                new_status=SrpRequest.Status.APPROVED,
                creator=request.user,
            )
            for srp_request in srp_request_list
        ]
        RequestComment.objects.bulk_create(comments)

        # Send notifications to the requesters
        for srp_request in srp_request_list:
            requester = srp_request.creator
            if not get_user_settings(user=requester).disable_notifications:
                logger.info(msg="Sending approval message to user")
                notify_requester(
                    requester=requester,
                    reviser=request.user,
                    srp_request=srp_request,
                    comment="",
                )

        # Return a success response
        return JsonResponse(
            data={"success": True, "message": _("SRP requests have been approved")},
            safe=False,
        )

    # Return an error response if the request method is not POST
    return JsonResponse(
        data={"success": False, "message": _("Invalid request method")},
        safe=False,
    )


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_request_deny(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Handle an AJAX request to deny a specific SRP (Ship Replacement Program) request.

    This view processes a POST request to reject an SRP request identified by its unique SRP code and request code.
    It validates the request, updates the request status, creates comments for the rejection, and sends notifications
    to the requester.

    :param request: The HTTP request object containing metadata and POST data.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link.
    :type srp_code: str
    :param srp_request_code: The unique code identifying the SRP request.
    :type srp_request_code: str
    :return: A JSON response indicating whether the operation was successful.
    :rtype: JsonResponse
    """

    try:
        # Retrieve the SRP request based on the provided SRP code and request code
        srp_request = SrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )
    except SrpRequest.DoesNotExist:
        # Return an error response if the SRP request does not exist
        return JsonResponse(
            data={"success": False, "message": _("No matching SRP request found")},
            safe=False,
        )

    if request.method == "POST":
        # Initialize the rejection form with the POST data
        form = SrpRequestRejectForm(data=json.loads(request.body))

        # Validate the form data
        if not form.is_valid():
            return JsonResponse(
                data={"success": False, "message": _("Invalid form data")}, safe=False
            )

        # Extract the rejection comment from the form
        reject_info = form.cleaned_data["comment"]
        requester = srp_request.creator

        # Update the SRP request status to rejected and set the payout amount to zero
        srp_request.payout_amount = 0
        srp_request.request_status = SrpRequest.Status.REJECTED
        srp_request.save()

        # Create comments for the status change and rejection reason
        RequestComment.objects.bulk_create(
            [
                RequestComment(
                    srp_request=srp_request,
                    comment_type=RequestComment.Type.STATUS_CHANGE,
                    new_status=SrpRequest.Status.REJECTED,
                    creator=request.user,
                ),
                RequestComment(
                    comment=reject_info,
                    srp_request=srp_request,
                    comment_type=RequestComment.Type.REJECT_REASON,
                    creator=request.user,
                ),
            ]
        )

        # Send a notification to the requester if notifications are enabled
        if not get_user_settings(user=requester).disable_notifications:
            logger.info("Sending reject message to user")

            notify_requester(
                requester=requester,
                reviser=request.user,
                srp_request=srp_request,
                comment=reject_info,
                message_level="danger",
            )

        # Return a success response
        return JsonResponse(
            data={"success": True, "message": _("SRP request has been rejected")},
            safe=False,
        )

    # Return an error response if the request method is not POST
    return JsonResponse(
        data={"success": False, "message": _("Invalid request method")},
        safe=False,
    )


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_request_remove(
    request: WSGIRequest,  # pylint: disable=unused-argument
    srp_code: str,
    srp_request_code: str,
) -> JsonResponse:
    """
    Handle an AJAX request to remove a specific SRP (Ship Replacement Program) request.

    This view processes a request to delete an SRP request identified by its unique SRP code and request code.
    If the request exists, it is removed from the database. A JSON response is returned indicating the success
    or failure of the operation.

    :param request: The HTTP request object containing metadata about the request.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link.
    :type srp_code: str
    :param srp_request_code: The unique code identifying the SRP request.
    :type srp_request_code: str
    :return: A JSON response indicating whether the operation was successful.
    :rtype: JsonResponse
    """

    try:
        # Attempt to retrieve and delete the SRP request matching the provided codes
        SrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        ).delete()

        # Prepare a success response
        data = {"success": True, "message": _("SRP request has been removed")}
    except SrpRequest.DoesNotExist:
        # Prepare a failure response if the SRP request does not exist
        data = {"success": False, "message": _("No matching SRP request found")}

    # Return the JSON response
    return JsonResponse(data=data, safe=False)


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_requests_bulk_remove(request: WSGIRequest, srp_code: str) -> JsonResponse:
    """
    Handle an AJAX request to remove multiple SRP (Ship Replacement Program) requests.

    This view processes a POST request containing a list of SRP request codes to remove. It validates the input,
    retrieves the matching SRP requests, deletes them from the database, and returns a JSON response indicating
    the success or failure of the operation.

    :param request: The HTTP request object containing metadata and POST data.
    :type request: WSGIRequest
    :param srp_code: The unique code identifying the SRP link.
    :type srp_code: str
    :return: A JSON response indicating whether the operation was successful.
    :rtype: JsonResponse
    """

    if request.method == "POST":
        # Parse the request body to retrieve the list of SRP request codes
        request_body = json.loads(request.body)
        srp_request_codes = request_body.get("srp_request_codes")

        logger.debug(
            "Bulk removing SRP requests for code: %s, with request codes: %s",
            srp_code,
            srp_request_codes,
        )

        # Validate the input data
        if not srp_request_codes or not srp_code:
            return JsonResponse(
                data={"success": False, "message": _("Invalid form data")}, safe=False
            )

        # Retrieve the SRP requests that match the given codes
        srp_requests = SrpRequest.objects.filter(
            Q(request_code__in=srp_request_codes) & Q(srp_link__srp_code=srp_code)
        )

        logger.debug(
            "Found %d SRP requests to remove for code: %s",
            srp_requests.count(),
            srp_code,
        )

        # If no matching requests are found, return an error response
        if not srp_requests.exists():
            return JsonResponse(
                data={"success": False, "message": _("No matching SRP requests found")},
                safe=False,
            )

        # Delete the matching SRP requests
        srp_requests.delete()

        # Return a success response
        return JsonResponse(
            data={"success": True, "message": _("SRP requests have been removed")},
            safe=False,
        )

    # Return an error response if the request method is not POST
    return JsonResponse(
        data={"success": False, "message": _("Invalid request method")},
        safe=False,
    )
