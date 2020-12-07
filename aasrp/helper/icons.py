# coding=utf-8

"""
some helper functions
so we don't mess up other files too much
"""

from aasrp.models import AaSrpRequestStatus, AaSrpLink, AaSrpRequest

from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


@login_required
@permission_required(
    "aasrp.basic_access", "aasrp.manage_srp_requests", "aasrp.manage_srp"
)
def get_dashboard_action_icons(request, srp_link: AaSrpLink) -> str:
    """
    getting the action buttons for the dashboard view
    :param request:
    :param srp_link:
    """

    button_request_url = reverse("aasrp:request_srp", args=[srp_link.srp_code])
    actions = (
        '<a href="{btn_link}" '
        'class="btn btn-aasrp btn-success btn-sm" '
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
            'class="btn btn-aasrp btn-primary btn-sm" '
            'title="{btn_title}">{btn_icon}</a><br>'.format(
                btn_link=button_view_url,
                btn_icon='<i class="fas fa-eye"></i>',
                btn_title=_("View SRP Requests"),
            )
        )

        if request.user.has_perm("aasrp.manage_srp"):
            button_edit_url = reverse("aasrp:edit_srp_link", args=[srp_link.srp_code])
            actions += (
                '<a href="{btn_link}" '
                'class="btn btn-aasrp btn-info btn-sm" '
                'title="{btn_title}">{btn_icon}</a>'.format(
                    btn_link=button_edit_url,
                    btn_icon='<i class="far fa-newspaper"></i>',
                    btn_title=_("Add/Edit AAR Link"),
                )
            )

            if srp_link.srp_status == "Active":
                button_disable_url = reverse(
                    "aasrp:disable_srp_link", args=[srp_link.srp_code]
                )

                data_name = srp_link.srp_name + " (" + srp_link.srp_code + ")"

                actions += (
                    '<a class="btn btn-aasrp btn-warning btn-sm" '
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

            if srp_link.srp_status == "Closed":
                button_enable_url = reverse(
                    "aasrp:enable_srp_link", args=[srp_link.srp_code]
                )

                data_name = srp_link.srp_name + " (" + srp_link.srp_code + ")"

                actions += (
                    '<a class="btn btn-aasrp btn-success btn-sm" '
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
                '<a class="btn btn-aasrp btn-danger btn-sm" '
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
def get_srp_request_status_icon(request, srp_request: AaSrpRequest) -> str:
    """
    get status icon for srp request
    :param request:
    :param srp_request:
    :return:
    """

    srp_request_status_icon = (
        '<button class="btn btn-warning btn-sm" title="{request_status_icon_title}">'
        "{request_status_icon}"
        "</button>".format(
            request_status_icon='<i class="fas fa-clock"></i>',
            request_status_icon_title=_("Pending"),
        )
    )
    if srp_request.request_status == AaSrpRequestStatus.APPROVED:
        srp_request_status_icon = (
            '<button class="btn btn-success btn-sm" title="{request_status_icon_title}">'
            "{request_status_icon}"
            "</button>".format(
                request_status_icon='<i class="fas fa-thumbs-up"></i>',
                request_status_icon_title=_("Approved"),
            )
        )

    if srp_request.request_status == AaSrpRequestStatus.REJECTED:
        srp_request_status_icon = (
            '<button class="btn btn-danger btn-sm" title="{request_status_icon_title}">'
            "{request_status_icon}"
            "</button>".format(
                request_status_icon='<i class="fas fa-thumbs-down"></i>',
                request_status_icon_title=_("Rejected"),
            )
        )

    return srp_request_status_icon


@login_required
@permission_required("aasrp.manage_srp_requests", "aasrp.manage_srp")
def get_srp_request_action_icons(request, srp_request: AaSrpRequest) -> str:
    """
    get action icons for srp requests
    :param request:
    :param srp_request:
    """

    # accept
    button_request_accept_url = reverse(
        "aasrp:request_srp", args=[srp_request.request_code]
    )
    actions = (
        '<a href="{btn_link}" '
        'class="btn btn-aasrp btn-success btn-sm" '
        'title="{btn_title}">{btn_icon}</a>'.format(
            btn_link=button_request_accept_url,
            btn_icon='<i class="fas fa-check"></i>',
            btn_title=_("Accept SRP Request"),
        )
    )

    # reject
    button_request_reject_url = reverse(
        "aasrp:request_srp", args=[srp_request.request_code]
    )
    actions += (
        '<a href="{btn_link}" '
        'class="btn btn-aasrp btn-warning btn-sm" '
        'title="{btn_title}">{btn_icon}</a>'.format(
            btn_link=button_request_reject_url,
            btn_icon='<i class="fas fa-ban"></i>',
            btn_title=_("Reject SRP Request"),
        )
    )

    # delete
    if request.user.has_perm("aasrp.manage_srp"):
        button_request_delete_url = reverse(
            "aasrp:request_srp", args=[srp_request.request_code]
        )
        actions += (
            '<a href="{btn_link}" '
            'class="btn btn-aasrp btn-danger btn-sm" '
            'title="{btn_title}">{btn_icon}</a>'.format(
                btn_link=button_request_delete_url,
                btn_icon='<i class="fas fa-trash-alt"></i>',
                btn_title=_("Remove SRP Request"),
            )
        )

    return actions
