# coding=utf-8

"""
some helper functions
so we don't mess up other files too much
"""

from aasrp.models import AaSrpRequestStatus, AaSrpLink, AaSrpRequest, AaSrpStatus

from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


@login_required
@permission_required(
    "aasrp.basic_access", "aasrp.manage_srp_requests", "aasrp.manage_srp"
)
def get_dashboard_action_icons(request: WSGIRequest, srp_link: AaSrpLink) -> str:
    """
    getting the action buttons for the dashboard view
    :param request:
    :param srp_link:
    """

    actions = ""

    if srp_link.srp_status == AaSrpStatus.ACTIVE:
        button_request_url = reverse("aasrp:request_srp", args=[srp_link.srp_code])
        actions += (
            '<a href="{btn_link}" '
            'class="btn btn-success btn-sm btn-icon-aasrp" '
            'title="{btn_title}">{btn_icon}</a>'.format(
                btn_link=button_request_url,
                btn_icon='<i class="fas fa-hand-holding-usd"></i>',
                btn_title=_("Request SRP"),
            )
        )

    if request.user.has_perm("aasrp.manage_srp") or request.user.has_perm(
        "aasrp.manage_srp_requests"
    ):
        button_view_url = reverse("aasrp:view_srp_requests", args=[srp_link.srp_code])
        actions += (
            '<a href="{btn_link}" '
            'class="btn btn-primary btn-sm btn-icon-aasrp" '
            'title="{btn_title}">{btn_icon}</a><br>'.format(
                btn_link=button_view_url,
                btn_icon='<i class="fas fa-eye"></i>',
                btn_title=_("View SRP Requests"),
            )
        )

        if srp_link.srp_status != AaSrpStatus.COMPLETED:
            if request.user.has_perm("aasrp.manage_srp"):
                if srp_link.srp_status == AaSrpStatus.ACTIVE:
                    button_edit_url = reverse(
                        "aasrp:edit_srp_link", args=[srp_link.srp_code]
                    )
                    actions += (
                        '<a href="{btn_link}" '
                        'class="btn btn-info btn-sm btn-icon-aasrp" '
                        'title="{btn_title}">{btn_icon}</a>'.format(
                            btn_link=button_edit_url,
                            btn_icon='<i class="far fa-newspaper"></i>',
                            btn_title=_("Add/Edit AAR Link"),
                        )
                    )

                    button_disable_url = reverse(
                        "aasrp:disable_srp_link", args=[srp_link.srp_code]
                    )

                    data_name = srp_link.srp_name + " (" + srp_link.srp_code + ")"

                    actions += (
                        '<a class="btn btn-warning btn-sm btn-icon-aasrp" '
                        'title="{btn_title}" '
                        'data-toggle="modal" '
                        'data-target="#{modal_id}" '
                        'data-url="{data_url}" '
                        'data-name="{data_name}">{btn_icon}</a>'.format(
                            data_url=button_disable_url,
                            data_name=data_name,
                            btn_icon='<i class="fas fa-ban"></i>',
                            btn_title=_("Disable SRP Link"),
                            modal_id="disable-srp-link",
                        )
                    )

                if srp_link.srp_status == AaSrpStatus.CLOSED:
                    button_enable_url = reverse(
                        "aasrp:enable_srp_link", args=[srp_link.srp_code]
                    )

                    data_name = srp_link.srp_name + " (" + srp_link.srp_code + ")"

                    actions += (
                        '<a class="btn btn-success btn-sm btn-icon-aasrp" '
                        'title="{btn_title}" '
                        'data-toggle="modal" '
                        'data-target="#{modal_id}" '
                        'data-url="{data_url}" '
                        'data-name="{data_name}">{btn_icon}</a>'.format(
                            data_url=button_enable_url,
                            data_name=data_name,
                            btn_icon='<i class="fas fa-check"></i>',
                            btn_title=_("Enable SRP Link"),
                            modal_id="enable-srp-link",
                        )
                    )

                button_remove_url = reverse(
                    "aasrp:delete_srp_link", args=[srp_link.srp_code]
                )

                data_name = srp_link.srp_name + " (" + srp_link.srp_code + ")"

                actions += (
                    '<a class="btn btn-danger btn-sm btn-icon-aasrp" '
                    'title="{btn_title}" '
                    'data-toggle="modal" '
                    'data-target="#{modal_id}" '
                    'data-url="{data_url}" '
                    'data-name="{data_name}">{btn_icon}</a>'.format(
                        data_url=button_remove_url,
                        data_name=data_name,
                        btn_icon='<i class="far fa-trash-alt"></i>',
                        btn_title=_("Remove SRP Link"),
                        modal_id="delete-srp-link",
                    )
                )

    return actions


@login_required
@permission_required("aasrp.basic_access")
def get_srp_request_status_icon(request: WSGIRequest, srp_request: AaSrpRequest) -> str:
    """
    get status icon for srp request
    :param request:
    :param srp_request:
    :return:
    """

    srp_request_status_icon = (
        '<button class="btn btn-warning btn-sm btn-icon-aasrp btn-icon-aasrp-status" '
        'title="{request_status_icon_title}">'
        "{request_status_icon}"
        "</button>".format(
            request_status_icon='<i class="fas fa-clock"></i>',
            request_status_icon_title=_("SRP Request Pending"),
        )
    )
    if srp_request.request_status == AaSrpRequestStatus.APPROVED:
        srp_request_status_icon = (
            '<button class="btn btn-success btn-sm btn-icon-aasrp btn-icon-aasrp-status" '
            'title="{request_status_icon_title}">'
            "{request_status_icon}"
            "</button>".format(
                request_status_icon='<i class="fas fa-thumbs-up"></i>',
                request_status_icon_title=_("SRP Request Approved"),
            )
        )

    if srp_request.request_status == AaSrpRequestStatus.REJECTED:
        srp_request_status_icon = (
            '<button class="btn btn-danger btn-sm btn-icon-aasrp btn-icon-aasrp-status" '
            'title="{request_status_icon_title}">'
            "{request_status_icon}"
            "</button>".format(
                request_status_icon='<i class="fas fa-thumbs-down"></i>',
                request_status_icon_title=_("SRP Request Rejected"),
            )
        )

    return srp_request_status_icon


@login_required
@permission_required("aasrp.manage_srp_requests", "aasrp.manage_srp")
def get_srp_request_action_icons(
    request: WSGIRequest, srp_link: AaSrpLink, srp_request: AaSrpRequest
) -> str:
    """
    get action icons for srp requests
    :param request:
    :param srp_code:
    :param srp_request:
    """

    actions = ""

    # read details
    button_request_details_url = reverse(
        "aasrp:ajax_srp_request_additional_information",
        args=[srp_link.srp_code, srp_request.request_code],
    )
    actions += (
        '<button data-link="{link}" '
        'data-toggle="modal" '
        'data-target="#srp-request-details" '
        'data-modal-title="{title}" '
        'data-modal-button-confirm="{modal_button_confirm}" '
        'class="btn btn-primary btn-sm btn-icon-aasrp" '
        'title="{title}">{icon}</button>'.format(
            link=button_request_details_url,
            icon='<i class="fas fa-info-circle"></i>',
            title=_("SRP Request Details"),
            modal_button_confirm=_("{fa_icon} Close").format(fa_icon=""),
        )
    )

    if srp_link.srp_status == AaSrpStatus.ACTIVE:
        # accept
        button_request_accept_url = reverse(
            "aasrp:ajax_srp_request_approve",
            args=[srp_link.srp_code, srp_request.request_code],
        )

        button_request_accept_state = ""
        if srp_request.request_status == AaSrpRequestStatus.APPROVED:
            button_request_accept_state = ' disabled="disabled"'

        actions += (
            '<button data-link="{link}" '
            'data-toggle="modal" '
            'data-target="#srp-request-accept" '
            'data-modal-title="{title}" '
            'data-modal-body="{modal_body}" '
            'data-modal-button-cancel="{modal_button_cancel}" '
            'data-modal-button-confirm="{modal_button_confirm}" '
            'data-modal-button-confirm-classes="{modal_button_confirm_classes}" '
            'class="btn btn-success btn-sm btn-icon-aasrp" '
            'title="{title}"{button_state}>{icon}</button>'.format(
                link=button_request_accept_url,
                icon='<i class="fas fa-check"></i>',
                title=_("Accept SRP Request"),
                modal_body=_("Are you sure you want to accept this SRP request?"),
                modal_button_cancel=_("{fa_icon} Cancel").format(
                    fa_icon="<i class='far fa-hand-paper'></i>"
                ),
                modal_button_confirm=_("{fa_icon} Accept SRP Request").format(
                    fa_icon="<i class='fas fa-check'></i>"
                ),
                modal_button_confirm_classes="btn btn-success btn-sm",
                button_state=button_request_accept_state,
            )
        )

        # reject
        button_request_reject_url = reverse(
            "aasrp:ajax_srp_request_deny",
            args=[srp_link.srp_code, srp_request.request_code],
        )

        button_request_reject_state = ""
        if srp_request.request_status == AaSrpRequestStatus.REJECTED:
            button_request_reject_state = ' disabled="disabled"'

        actions += (
            '<button data-link="{link}" '
            'data-toggle="modal" '
            'data-target="#srp-request-reject" '
            'data-modal-title="{title}" '
            'data-modal-body="{modal_body}" '
            'data-modal-button-cancel="{modal_button_cancel}" '
            'data-modal-button-confirm="{modal_button_confirm}" '
            'data-modal-button-confirm-classes="{modal_button_confirm_classes}" '
            'class="btn btn-warning btn-sm btn-icon-aasrp" '
            'title="{title}"{button_state}>{icon}</button>'.format(
                link=button_request_reject_url,
                icon='<i class="fas fa-ban"></i>',
                title=_("Reject SRP Request"),
                modal_body=_("Are you sure you want to reject this SRP request?"),
                modal_button_cancel=_("{fa_icon} Cancel").format(
                    fa_icon="<i class='far fa-hand-paper'></i>"
                ),
                modal_button_confirm=_("{fa_icon} Reject SRP Request").format(
                    fa_icon="<i class='fas fa-ban'></i>"
                ),
                modal_button_confirm_classes="btn btn-warning btn-sm",
                button_state=button_request_reject_state,
            )
        )

        # delete
        if request.user.has_perm("aasrp.manage_srp"):
            button_request_delete_url = reverse(
                "aasrp:ajax_srp_request_remove",
                args=[srp_link.srp_code, srp_request.request_code],
            )
            actions += (
                '<button data-link="{link}" '
                'data-toggle="modal" '
                'data-target="#srp-link-action-modal" '
                'data-modal-title="{title}" '
                'data-modal-body="{modal_body}" '
                'data-modal-button-cancel="{modal_button_cancel}" '
                'data-modal-button-confirm="{modal_button_confirm}" '
                'data-modal-button-confirm-classes="{modal_button_confirm_classes}" '
                'class="btn btn-danger btn-sm btn-icon-aasrp" '
                'title="{title}">{icon}</button>'.format(
                    link=button_request_delete_url,
                    icon='<i class="fas fa-trash-alt"></i>',
                    title=_("Remove SRP Request"),
                    modal_body=_("Are you sure you want to remove this SRP request?"),
                    modal_button_cancel=_("{fa_icon} Cancel").format(
                        fa_icon="<i class='far fa-hand-paper'></i>"
                    ),
                    modal_button_confirm=_("{fa_icon} Remove SRP Request").format(
                        fa_icon="<i class='fas fa-trash-alt'></i>"
                    ),
                    modal_button_confirm_classes="btn btn-danger btn-sm",
                )
            )

    return actions
