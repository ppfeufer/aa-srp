# coding=utf-8

"""
some helper functions
so we don't mess up views.py too much
"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def get_dashboard_action_buttons(request, srp_link):
    """
    getting the action buttons for the dashboard view
    :param request:
    :param srp_link:
    """

    button_request_url = reverse("aasrp:request_srp", args=[srp_link.srp_code])
    # button_request_url = "#"
    actions = '<a href="{btn_link}" class="btn btn-aasrp btn-success btn-sm" title="{btn_title}">{btn_icon}</a>'.format(
        btn_link=button_request_url,
        btn_icon='<i class="fas fa-hand-holding-usd"></i>',
        btn_title=_("Request SRP"),
    )

    if request.user.has_perm("aasrp.manage_srp") or request.user.has_perm(
        "aasrp.manage_srp_requests"
    ):
        button_view_url = "#"
        actions += '<a href="{btn_link}" class="btn btn-aasrp btn-primary btn-sm" title="{btn_title}">{btn_icon}</a><br>'.format(
            btn_link=button_view_url,
            btn_icon='<i class="fas fa-eye"></i>',
            btn_title=_("View SRP Link"),
        )

        if request.user.has_perm("aasrp.manage_srp"):
            button_edit_url = "#"
            actions += '<a href="{btn_link}" class="btn btn-aasrp btn-info btn-sm" title="{btn_title}">{btn_icon}</a>'.format(
                btn_link=button_edit_url,
                btn_icon='<i class="fas fa-pencil-alt"></i>',
                btn_title=_("Edit SRP Link"),
            )

            if srp_link.srp_status == "Active":
                button_disable_url = "#"
                actions += '<a href="{btn_link}" class="btn btn-aasrp btn-warning btn-sm" title="{btn_title}">{btn_icon}</a>'.format(
                    btn_link=button_disable_url,
                    btn_icon='<i class="fas fa-ban"></i>',
                    btn_title=_("Disable SRP Link"),
                )

            if srp_link.srp_status == "Closed":
                button_disable_url = "#"
                actions += '<a href="{btn_link}" class="btn btn-aasrp btn-success btn-sm" title="{btn_title}">{btn_icon}</a>'.format(
                    btn_link=button_disable_url,
                    btn_icon='<i class="fas fa-check"></i>',
                    btn_title=_("Enable SRP Link"),
                )

            button_remove_url = "#"
            actions += '<a href="{btn_link}" class="btn btn-aasrp btn-danger btn-sm" title="{btn_title}">{btn_icon}</a>'.format(
                btn_link=button_remove_url,
                btn_icon='<i class="far fa-trash-alt"></i>',
                btn_title=_("Remove SRP Link"),
            )

    return actions
