"""
Some helper functions, so we don't mess up other files too much
"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required

# AA SRP
from aasrp.models import SrpLink, SrpRequest


@login_required
@permission_required("aasrp.basic_access")
def get_dashboard_action_icons(request: WSGIRequest, srp_link: SrpLink) -> str:
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

    if srp_link.srp_status == SrpLink.Status.ACTIVE:
        button_request_url = reverse(
            viewname="aasrp:request_srp", args=[srp_link.srp_code]
        )
        btn_icon = '<i class="fa-solid fa-hand-holding-dollar"></i>'
        btn_title = _("Request SRP")
        actions += (
            f'<a href="{button_request_url}" '
            'class="btn btn-success btn-sm btn-icon-aasrp" '
            f'title="{btn_title}" data-bs-tooltip="aa-srp">{btn_icon}</a>'
        )

    if request.user.has_perm("aasrp.manage_srp") or request.user.has_perm(
        "aasrp.manage_srp_requests"
    ):
        button_view_url = reverse(
            viewname="aasrp:view_srp_requests", args=[srp_link.srp_code]
        )
        btn_icon = '<i class="fa-solid fa-eye"></i>'
        btn_title = _("View SRP requests")
        actions += (
            f'<a href="{button_view_url}" '
            'class="btn btn-primary btn-sm btn-icon-aasrp" '
            f'title="{btn_title}" data-bs-tooltip="aa-srp">{btn_icon}</a><br>'
        )

        if srp_link.srp_status != SrpLink.Status.COMPLETED:
            if request.user.has_perm("aasrp.manage_srp"):
                if srp_link.srp_status == SrpLink.Status.ACTIVE:
                    button_edit_url = reverse(
                        viewname="aasrp:edit_srp_link", args=[srp_link.srp_code]
                    )
                    btn_icon = '<i class="fa-regular fa-newspaper"></i>'
                    btn_title = _("Add/Change AAR link")
                    actions += (
                        f'<a href="{button_edit_url}" '
                        'class="btn btn-info btn-sm btn-icon-aasrp" '
                        f'title="{btn_title}" data-bs-tooltip="aa-srp">{btn_icon}</a>'
                    )

                    button_disable_url = reverse(
                        viewname="aasrp:disable_srp_link", args=[srp_link.srp_code]
                    )
                    btn_icon = '<i class="fa-solid fa-ban"></i>'
                    btn_title = _("Disable SRP link")
                    modal_id = "disable-srp-link"
                    data_name = srp_link.srp_name + " (" + srp_link.srp_code + ")"

                    actions += (
                        '<a class="btn btn-warning btn-sm btn-icon-aasrp" '
                        f'title="{btn_title}" '
                        'data-bs-tooltip="aa-srp" '
                        'data-bs-toggle="modal" '
                        f'data-bs-target="#{modal_id}" '
                        f'data-url="{button_disable_url}" '
                        f'data-name="{data_name}">{btn_icon}</a>'
                    )

                if srp_link.srp_status == SrpLink.Status.CLOSED:
                    button_enable_url = reverse(
                        viewname="aasrp:enable_srp_link", args=[srp_link.srp_code]
                    )
                    btn_icon = '<i class="fa-solid fa-check"></i>'
                    btn_title = _("Enable SRP link")
                    modal_id = "enable-srp-link"
                    data_name = srp_link.srp_name + " (" + srp_link.srp_code + ")"

                    actions += (
                        '<a class="btn btn-success btn-sm btn-icon-aasrp" '
                        f'title="{btn_title}" '
                        'data-bs-tooltip="aa-srp" '
                        'data-bs-toggle="modal" '
                        f'data-bs-target="#{modal_id}" '
                        f'data-url="{button_enable_url}" '
                        f'data-name="{data_name}">{btn_icon}</a>'
                    )

                button_remove_url = reverse(
                    viewname="aasrp:delete_srp_link", args=[srp_link.srp_code]
                )
                btn_icon = '<i class="fa-regular fa-trash-can"></i>'
                btn_title = _("Remove SRP ink")
                modal_id = "delete-srp-link"
                data_name = srp_link.srp_name + " (" + srp_link.srp_code + ")"

                actions += (
                    '<a class="btn btn-danger btn-sm btn-icon-aasrp" '
                    f'title="{btn_title}" '
                    'data-bs-tooltip="aa-srp" '
                    'data-bs-toggle="modal" '
                    f'data-bs-target="#{modal_id}" '
                    f'data-url="{button_remove_url}" '
                    f'data-name="{data_name}">{btn_icon}</a>'
                )

    return actions


@login_required
@permission_required("aasrp.basic_access")
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

    request_status_icon_title = _("SRP request pending")
    srp_request_status_icon = (
        '<button class="btn btn-info btn-sm btn-icon-aasrp btn-icon-aasrp-status" '
        f'title="{request_status_icon_title}" data-bs-tooltip="aa-srp">'
        '<i class="fa-solid fa-clock"></i>'
        "</button>"
    )

    if srp_request.request_status == SrpRequest.Status.APPROVED:
        btn_classes = "btn btn-success btn-sm btn-icon-aasrp btn-icon-aasrp-status"
        request_status_icon_title = _("SRP request approved")
        srp_request_status_icon = (
            f'<button class="{btn_classes}" '
            f'title="{request_status_icon_title}" data-bs-tooltip="aa-srp">'
            '<i class="fa-solid fa-thumbs-up"></i>'
            "</button>"
        )

    if srp_request.request_status == SrpRequest.Status.REJECTED:
        btn_classes = "btn btn-danger btn-sm btn-icon-aasrp btn-icon-aasrp-status"
        request_status_icon_title = _("SRP request rejected")
        srp_request_status_icon = (
            f'<button class="{btn_classes}" '
            f'title="{request_status_icon_title}" data-bs-tooltip="aa-srp">'
            '<i class="fa-solid fa-thumbs-down"></i>'
            "</button>"
        )

    return srp_request_status_icon


@login_required
@permission_required("aasrp.basic_access")
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


@login_required
@permission_required("aasrp.basic_access")
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

    button_request_accept_state = ""
    if srp_request.request_status == SrpRequest.Status.APPROVED:
        button_request_accept_state = ' disabled="disabled"'

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


@login_required
@permission_required("aasrp.basic_access")
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

    button_request_reject_state = ""
    if srp_request.request_status == SrpRequest.Status.REJECTED:
        button_request_reject_state = ' disabled="disabled"'

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


@login_required
@permission_required("aasrp.basic_access")
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


@login_required
@permissions_required(("aasrp.manage_srp_requests", "aasrp.manage_srp"))
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

        # Accept
        srp_request_action_icons += get_srp_request_accept_icon(
            request=request, srp_link=srp_link, srp_request=srp_request
        )

        # Reject
        srp_request_action_icons += get_srp_request_reject_icon(
            request=request, srp_link=srp_link, srp_request=srp_request
        )

        # Delete
        if request.user.has_perm("aasrp.manage_srp"):
            srp_request_action_icons += get_srp_request_delete_icon(
                request=request, srp_link=srp_link, srp_request=srp_request
            )

    return srp_request_action_icons
