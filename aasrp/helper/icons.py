"""
Some helper functions, so we don't mess up other files too much
"""

# Django
from django.core.handlers.wsgi import WSGIRequest
from django.template.loader import render_to_string
from django.urls import reverse
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
    title: str,
    modal_id: str = None,
    data_name: str = None,
):
    """
    Create a button with the given parameters

    :param url:
    :type url:
    :param btn_class:
    :type btn_class:
    :param icon_class:
    :type icon_class:
    :param title:
    :type title:
    :param modal_id:
    :type modal_id:
    :param data_name:
    :type data_name:
    :return:
    :rtype:
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
    Getting the action buttons for the dashboard view

    :param request:
    :type request:
    :param srp_link:
    :type srp_link:
    :return:
    :rtype:
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
    Get status icon for srp request

    :param request:
    :type request:
    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
    """

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

    btn_class, icon_class, request_status_icon_title = status_icons.get(
        srp_request.request_status, ("btn-info", "fa-clock", _("SRP request pending"))
    )

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
    Get details icon for an SRP request

    :param request:
    :type request:
    :param srp_link:
    :type srp_link:
    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
    """

    button_request_details_url = reverse(
        viewname="aasrp:ajax_srp_request_additional_information",
        args=[srp_link.srp_code, srp_request.request_code],
    )

    title = _("SRP request details")

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
    Get accept icon for an SRP request

    :param request:
    :type request:
    :param srp_link:
    :type srp_link:
    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
    """

    button_request_accept_url = reverse(
        viewname="aasrp:ajax_srp_request_approve",
        args=[srp_link.srp_code, srp_request.request_code],
    )

    button_request_accept_state = (
        ' disabled="disabled"'
        if srp_request.request_status == SrpRequest.Status.APPROVED
        else ""
    )

    modal_target = (
        "#srp-request-accept-rejected"
        if srp_request.request_status == SrpRequest.Status.REJECTED
        else "#srp-request-accept"
    )

    icon = '<i class="fa-solid fa-check"></i>'
    title = _("Accept SRP request")

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
    Get reject icon for an SRP request

    :param request:
    :type request:
    :param srp_link:
    :type srp_link:
    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
    """

    button_request_reject_url = reverse(
        viewname="aasrp:ajax_srp_request_deny",
        args=[srp_link.srp_code, srp_request.request_code],
    )

    button_request_reject_state = (
        ' disabled="disabled"'
        if srp_request.request_status == SrpRequest.Status.REJECTED
        else ""
    )

    icon = '<i class="fa-solid fa-ban"></i>'
    title = _("Reject SRP request")

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
    Get delete icon for an SRP request

    :param request:
    :type request:
    :param srp_link:
    :type srp_link:
    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
    """

    button_request_delete_url = reverse(
        viewname="aasrp:ajax_srp_request_remove",
        args=[srp_link.srp_code, srp_request.request_code],
    )

    icon = '<i class="fa-solid fa-trash-can"></i>'
    title = _("Delete SRP request")

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
    Get action icons for srp requests

    :param request:
    :type request:
    :param srp_link:
    :type srp_link:
    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
    """

    srp_request_action_icons = get_srp_request_details_icon(
        request=request, srp_link=srp_link, srp_request=srp_request
    )

    if srp_link.srp_status in (SrpLink.Status.ACTIVE, SrpLink.Status.CLOSED):
        srp_request_action_icons += "<br>"

        for icon_func in [get_srp_request_accept_icon, get_srp_request_reject_icon]:
            srp_request_action_icons += icon_func(
                request=request, srp_link=srp_link, srp_request=srp_request
            )

        if request.user.has_perm("aasrp.manage_srp"):
            srp_request_action_icons += get_srp_request_delete_icon(
                request=request, srp_link=srp_link, srp_request=srp_request
            )

    return srp_request_action_icons


def copy_to_clipboard_icon(data: str, title: str) -> SafeString:
    """
    Get copy to clipboard icon

    :param data: The data to be copied to the clipboard
    :type data: str
    :param title: The title for the icon
    :type title: str
    :return: The HTML for the copy to clipboard icon
    :rtype: SafeString
    """

    return render_to_string(
        template_name="aasrp/partials/common/copy-to-clipboard-icon.html",
        context={"data": data, "title": title},
    )
