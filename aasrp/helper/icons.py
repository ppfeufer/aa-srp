"""
This module contains helper functions to generate HTML elements and icons for the AA SRP application.

The functions in this module are designed to create reusable HTML components, such as buttons and icons,
to ensure consistency across the application. These components are used for actions like managing SRP links,
handling SRP requests, and copying data to the clipboard.
"""

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.functional import Promise
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required

# AA SRP
from aasrp.models import SrpLink, SrpRequest


def _create_button(  # pylint: disable=too-many-arguments, too-many-positional-arguments
    url: str,
    btn_class: str,
    icon_class: str,
    title: str | Promise,
    modal_id: str = None,
    data_name: str = None,
):
    """
    Generate an HTML button element with customizable attributes.

    This function creates an HTML button with the specified URL, CSS classes, icon, and optional modal attributes.
    It supports both standard links and modal-trigger buttons.

    :param url: The URL or data-url attribute for the button.
    :type url: str
    :param btn_class: The CSS class for styling the button.
    :type btn_class: str
    :param icon_class: The CSS class for the icon inside the button.
    :type icon_class: str
    :param title: The tooltip text for the button.
    :type title: str
    :param modal_id: The ID of the modal to be triggered (optional).
    :type modal_id: str, optional
    :param data_name: Additional data-name attribute for the button (optional).
    :type data_name: str, optional
    :return: The HTML string representing the button.
    :rtype: str
    """

    href_or_modal_attrs = (
        f'data-bs-toggle="modal" data-bs-target="#{modal_id}" data-name="{data_name}" data-url="{url}"'
        if modal_id
        else f'href="{url}"'
    )

    return (
        f'<a class="btn {btn_class} btn-sm btn-icon-aasrp" '
        f'title="{title}" data-bs-tooltip="aa-srp" {href_or_modal_attrs}>'
        f'<i class="{icon_class}"></i></a>'
    )


def dashboard_action_icons(request: WSGIRequest, srp_link: SrpLink) -> str:
    """
    Generate action buttons for the dashboard view.

    This function creates a set of HTML action buttons based on the status of the SRP link
    and the user's permissions. The buttons allow users to perform actions such as requesting SRP,
    viewing SRP requests, editing SRP links, and enabling/disabling or deleting SRP links.

    :param request: The HTTP request object, used to check user permissions.
    :type request: WSGIRequest
    :param srp_link: The SRP link object containing information about the SRP status and code.
    :type srp_link: SrpLink
    :return: A string containing the HTML for the action buttons.
    :rtype: str
    """

    actions = ""

    # Active SRP link
    if srp_link.srp_status == SrpLink.Status.ACTIVE:
        # Add SRP request button
        actions += _create_button(
            url=reverse(viewname="aasrp:request_srp", args=[srp_link.srp_code]),
            btn_class="btn btn-success",
            icon_class="fa-solid fa-hand-holding-dollar",
            title=_("Request SRP"),
        )

    # Check if the user has permission to manage SRP links or requests
    if request.user.has_perm(perm="aasrp.manage_srp") or request.user.has_perm(
        perm="aasrp.manage_srp_requests"
    ):
        # Add view SRP requests button
        actions += (
            _create_button(
                url=reverse(
                    viewname="aasrp:view_srp_requests", args=[srp_link.srp_code]
                ),
                btn_class="btn btn-primary",
                icon_class="fa-solid fa-eye",
                title=_("View SRP requests"),
            )
            + "<br>"
        )

        # Whether the SRP link is active or closed, we can edit it
        if srp_link.srp_status != SrpLink.Status.COMPLETED and request.user.has_perm(
            "aasrp.manage_srp"
        ):
            # Check if the SRP status is active
            if srp_link.srp_status == SrpLink.Status.ACTIVE:
                # Add AAR link button
                actions += _create_button(
                    url=reverse(
                        viewname="aasrp:edit_srp_link", args=[srp_link.srp_code]
                    ),
                    btn_class="btn btn-info",
                    icon_class="fa-regular fa-newspaper",
                    title=_("Add/Change AAR link"),
                )
                # Add disable SRP link button
                actions += _create_button(
                    url=reverse(
                        viewname="aasrp:disable_srp_link", args=[srp_link.srp_code]
                    ),
                    btn_class="btn btn-warning",
                    icon_class="fa-solid fa-ban",
                    title=_("Disable SRP link"),
                    modal_id="disable-srp-link",
                    data_name=f"{srp_link.srp_name} ({srp_link.srp_code})",
                )

            # Check if the SRP status is closed
            if srp_link.srp_status == SrpLink.Status.CLOSED:
                # Add enable SRP link button
                actions += _create_button(
                    url=reverse(
                        viewname="aasrp:enable_srp_link", args=[srp_link.srp_code]
                    ),
                    btn_class="btn btn-success",
                    icon_class="fa-solid fa-check",
                    title=_("Enable SRP link"),
                    modal_id="enable-srp-link",
                    data_name=f"{srp_link.srp_name} ({srp_link.srp_code})",
                )

            # Add delete SRP link button
            actions += _create_button(
                url=reverse(viewname="aasrp:delete_srp_link", args=[srp_link.srp_code]),
                btn_class="btn btn-danger",
                icon_class="fa-regular fa-trash-can",
                title=_("Remove SRP link"),
                modal_id="delete-srp-link",
                data_name=f"{srp_link.srp_name} ({srp_link.srp_code})",
            )

    return actions


def get_srp_request_status_icon(
    request: WSGIRequest, srp_request: SrpRequest  # pylint: disable=unused-argument
) -> str:
    """
    Generate an HTML button representing the status of an SRP request.

    This function creates an HTML button with a specific style and icon based on the status
    of the given SRP request. The button includes a tooltip describing the status.

    :param request: The HTTP request object (not used in this function).
    :type request: WSGIRequest
    :param srp_request: The SRP request object containing the status information.
    :type srp_request: SrpRequest
    :return: An HTML string representing the status icon button.
    :rtype: str
    """

    # Define the mapping of SRP request statuses to button classes, icons, and tooltips
    status_icons = {
        SrpRequest.Status.PENDING: ("btn-info", "fa-clock", _("SRP request pending")),
        SrpRequest.Status.APPROVED: (
            "btn-success",
            "fa-thumbs-up",
            _("SRP request approved"),
        ),
        SrpRequest.Status.REJECTED: (
            "btn-danger",
            "fa-thumbs-down",
            _("SRP request rejected"),
        ),
    }

    # Get the button class, icon class, and tooltip for the current status
    btn_class, icon_class, request_status_icon_title = status_icons.get(
        srp_request.request_status, ("btn-info", "fa-clock", _("SRP request pending"))
    )

    # Generate the HTML for the status icon button
    srp_request_status_icon = (
        f'<button class="btn {btn_class} btn-sm btn-icon-aasrp btn-icon-aasrp-status cursor-default" '
        f'title="{request_status_icon_title}" data-bs-tooltip="aa-srp">'
        f'<i class="fa-solid {icon_class}"></i>'
        "</button>"
    )

    return srp_request_status_icon


def get_srp_request_details_icon(
    request: WSGIRequest,  # pylint: disable=unused-argument
    srp_link: SrpLink,
    srp_request: SrpRequest,
) -> str:
    """
    Generate an HTML button for viewing SRP request details.

    This function creates an HTML button that, when clicked, opens a modal displaying
    additional information about a specific SRP request. The button includes a tooltip
    and uses Bootstrap classes for styling.

    :param request: The HTTP request object (not used in this function).
    :type request: WSGIRequest
    :param srp_link: The SRP link object associated with the SRP request.
    :type srp_link: SrpLink
    :param srp_request: The SRP request object containing the request details.
    :type srp_request: SrpRequest
    :return: An HTML string representing the details icon button.
    :rtype: str
    """

    # Generate the URL for fetching additional information about the SRP request
    button_request_details_url = reverse(
        viewname="aasrp:ajax_srp_request_additional_information",
        args=[srp_link.srp_code, srp_request.request_code],
    )

    # Tooltip title for the button
    title = _("SRP request details")

    # Create the HTML for the details icon button
    srp_request_details_icon = (
        f'<button data-link="{button_request_details_url}" '
        'data-bs-tooltip="aa-srp" '
        'data-bs-toggle="modal" '
        'data-bs-target="#srp-request-details" '
        'class="btn btn-primary btn-sm btn-icon-aasrp" '
        f'title="{title}"><i class="fa-solid fa-circle-info"></i></button>'
    )

    return srp_request_details_icon


def get_srp_request_accept_icon(
    request: WSGIRequest,  # pylint: disable=unused-argument
    srp_link: SrpLink,
    srp_request: SrpRequest,
) -> str:
    """
    Generate an HTML button for accepting an SRP request.

    This function creates an HTML button that allows users to approve an SRP request.
    The button's state and modal target are determined based on the current status of the SRP request.
    If the request is already approved, the button is disabled. The button includes a tooltip
    and uses Bootstrap classes for styling.

    :param request: The HTTP request object (not used in this function).
    :type request: WSGIRequest
    :param srp_link: The SRP link object associated with the SRP request.
    :type srp_link: SrpLink
    :param srp_request: The SRP request object containing the request details.
    :type srp_request: SrpRequest
    :return: An HTML string representing the accept icon button.
    :rtype: str
    """

    # Generate the URL for approving the SRP request
    button_request_accept_url = reverse(
        viewname="aasrp:ajax_srp_request_approve",
        args=[srp_link.srp_code, srp_request.request_code],
    )

    # Determine if the button should be disabled based on the request status
    button_request_accept_state = (
        ' disabled="disabled"'
        if srp_request.request_status == SrpRequest.Status.APPROVED
        else ""
    )

    # Set the modal target based on the request status
    modal_target = (
        "#srp-request-accept-rejected"
        if srp_request.request_status == SrpRequest.Status.REJECTED
        else "#srp-request-accept"
    )

    # Define the icon and tooltip title for the button
    icon = '<i class="fa-solid fa-check"></i>'
    title = _("Accept SRP request")

    # Create the HTML for the accept icon button
    srp_request_accept_icon = (
        f'<button data-link="{button_request_accept_url}" '
        'data-bs-tooltip="aa-srp" '
        'data-bs-toggle="modal" '
        f'data-bs-target="{modal_target}" '
        'class="btn btn-success btn-sm btn-icon-aasrp" '
        f'title="{title}"{button_request_accept_state}>{icon}</button>'
    )

    return srp_request_accept_icon


def get_srp_request_reject_icon(
    request: WSGIRequest,  # pylint: disable=unused-argument
    srp_link: SrpLink,
    srp_request: SrpRequest,
) -> str:
    """
    Generate an HTML button for rejecting an SRP request.

    This function creates an HTML button that allows users to reject an SRP request.
    The button's state is determined based on the current status of the SRP request.
    If the request is already rejected, the button is disabled. The button includes a tooltip
    and uses Bootstrap classes for styling.

    :param request: The HTTP request object (not used in this function).
    :type request: WSGIRequest
    :param srp_link: The SRP link object associated with the SRP request.
    :type srp_link: SrpLink
    :param srp_request: The SRP request object containing the request details.
    :type srp_request: SrpRequest
    :return: An HTML string representing the reject icon button.
    :rtype: str
    """

    # Generate the URL for rejecting the SRP request
    button_request_reject_url = reverse(
        viewname="aasrp:ajax_srp_request_deny",
        args=[srp_link.srp_code, srp_request.request_code],
    )

    # Determine if the button should be disabled based on the request status
    button_request_reject_state = (
        ' disabled="disabled"'
        if srp_request.request_status == SrpRequest.Status.REJECTED
        else ""
    )

    # Define the icon and tooltip title for the button
    icon = '<i class="fa-solid fa-ban"></i>'
    title = _("Reject SRP request")

    # Create the HTML for the reject icon button
    srp_request_reject_icon = (
        f'<button data-link="{button_request_reject_url}" '
        'data-bs-tooltip="aa-srp" '
        'data-bs-toggle="modal" '
        'data-bs-target="#srp-request-reject" '
        'class="btn btn-warning btn-sm btn-icon-aasrp" '
        f'title="{title}"{button_request_reject_state}>{icon}</button>'
    )

    return srp_request_reject_icon


def get_srp_request_delete_icon(
    request: WSGIRequest,  # pylint: disable=unused-argument
    srp_link: SrpLink,
    srp_request: SrpRequest,
) -> str:
    """
    Generate an HTML button for deleting an SRP request.

    This function creates an HTML button that allows users to delete an SRP request.
    The button includes a tooltip and uses Bootstrap classes for styling. When clicked,
    it triggers a modal for confirming the deletion.

    :param request: The HTTP request object (not used in this function).
    :type request: WSGIRequest
    :param srp_link: The SRP link object associated with the SRP request.
    :type srp_link: SrpLink
    :param srp_request: The SRP request object containing the request details.
    :type srp_request: SrpRequest
    :return: An HTML string representing the delete icon button.
    :rtype: str
    """

    # Generate the URL for deleting the SRP request
    button_request_delete_url = reverse(
        viewname="aasrp:ajax_srp_request_remove",
        args=[srp_link.srp_code, srp_request.request_code],
    )

    # Define the icon and tooltip title for the button
    icon = '<i class="fa-solid fa-trash-can"></i>'
    title = _("Delete SRP request")

    # Create the HTML for the delete icon button
    srp_request_delete_icon = (
        f'<button data-link="{button_request_delete_url}" '
        'data-bs-tooltip="aa-srp" '
        'data-bs-toggle="modal" '
        'data-bs-target="#srp-request-remove" '
        'class="btn btn-danger btn-sm btn-icon-aasrp" '
        f'title="{title}">{icon}</button>'
    )

    return srp_request_delete_icon


@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def get_srp_request_action_icons(
    request: WSGIRequest, srp_link: SrpLink, srp_request: SrpRequest
) -> str:
    """
    Generate HTML action icons for SRP requests.

    This function creates a set of HTML action buttons for a specific SRP request. The buttons
    include options for viewing details, accepting, rejecting, and deleting the request, depending
    on the SRP link's status and the user's permissions.

    :param request: The HTTP request object, used to check user permissions.
    :type request: WSGIRequest
    :param srp_link: The SRP link object associated with the SRP request.
    :type srp_link: SrpLink
    :param srp_request: The SRP request object containing the request details.
    :type srp_request: SrpRequest
    :return: A string containing the HTML for the action icons.
    :rtype: str
    """

    # Generate the details icon for the SRP request
    srp_request_action_icons = get_srp_request_details_icon(
        request=request, srp_link=srp_link, srp_request=srp_request
    )

    # Add additional action icons if the SRP link is active or closed
    if srp_link.srp_status in (SrpLink.Status.ACTIVE, SrpLink.Status.CLOSED):
        srp_request_action_icons += "<br>"

        # Add accept and reject icons for the SRP request
        for icon_func in [get_srp_request_accept_icon, get_srp_request_reject_icon]:
            srp_request_action_icons += icon_func(
                request=request, srp_link=srp_link, srp_request=srp_request
            )

        # Add delete icon if the user has permission to manage SRP
        if request.user.has_perm("aasrp.manage_srp"):
            srp_request_action_icons += get_srp_request_delete_icon(
                request=request, srp_link=srp_link, srp_request=srp_request
            )

    return srp_request_action_icons


def copy_to_clipboard_icon(data: str, title: str | Promise) -> SafeString:
    """
    Generate an HTML icon for copying data to the clipboard.

    This function renders an HTML template for a "copy to clipboard" icon. The icon,
    when clicked, copies the specified data to the user's clipboard. It includes a
    tooltip with the provided title for better user experience.

    :param data: The data to be copied to the clipboard.
    :type data: str
    :param title: The tooltip text for the icon.
    :type title: str | Promise
    :return: The HTML string for the copy to clipboard icon.
    :rtype: SafeString
    """

    return render_to_string(
        template_name="aasrp/partials/common/copy-to-clipboard-icon.html",
        context={"data": data, "title": title},
    )
