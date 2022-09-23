"""
aasrp url config
"""

# Django
from django.urls import include, path

# AA SRP
from aasrp import views

app_name: str = "aasrp"

urlpatterns = [
    path(route="", view=views.dashboard, name="dashboard"),
    path(
        route="all/", view=views.dashboard, kwargs={"show_all_links": True}, name="all"
    ),
    path(route="add/", view=views.srp_link_add, name="add_srp_link"),
    path(
        route="srp-link/<str:srp_code>/edit/",
        view=views.srp_link_edit,
        name="edit_srp_link",
    ),
    path(
        route="srp-link/<str:srp_code>/view-srp-requests/",
        view=views.srp_link_view_requests,
        name="view_srp_requests",
    ),
    path(
        route="srp-link/<str:srp_code>/enable/",
        view=views.enable_srp_link,
        name="enable_srp_link",
    ),
    path(
        route="srp-link/<str:srp_code>/disable/",
        view=views.disable_srp_link,
        name="disable_srp_link",
    ),
    path(
        route="srp-link/<str:srp_code>/delete/",
        view=views.delete_srp_link,
        name="delete_srp_link",
    ),
    path(
        route="srp-link/<str:srp_code>/request-srp/",
        view=views.request_srp,
        name="request_srp",
    ),
    path(
        route="srp-link/<str:srp_code>/complete/",
        view=views.complete_srp_link,
        name="complete_srp_link",
    ),
    # Ajax calls
    path(
        route="ajax/",
        view=include(
            [
                path(
                    # Get active SRP links
                    route="active-srp-links-data/",
                    view=views.ajax_dashboard_srp_links_data,
                    name="ajax_dashboard_srp_links_data",
                ),
                path(
                    # Get all SRP links
                    route="active-srp-links-data/all/",
                    view=views.ajax_dashboard_srp_links_data,
                    kwargs={"show_all_links": True},
                    name="ajax_dashboard_srp_links_all_data",
                ),
                path(
                    # Get all SRP request for the current user
                    route="user-srp-requests-data/",
                    view=views.ajax_dashboard_user_srp_requests_data,
                    name="ajax_dashboard_user_srp_requests_data",
                ),
                path(
                    # Get all SRP requests for the current SRP link
                    route="srp-link/<str:srp_code>/view-srp-requests-data/",
                    view=views.ajax_srp_link_view_requests_data,
                    name="ajax_srp_link_view_requests_data",
                ),
                path(
                    # Get addition information for the current SRP request
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/view-additional-information-data/"
                    ),
                    view=views.ajax_srp_request_additional_information,
                    name="ajax_srp_request_additional_information",
                ),
                path(
                    # Change the SRP payout amount
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/change-srp-payout/"
                    ),
                    view=views.ajax_srp_request_change_payout,
                    name="ajax_srp_request_change_payout",
                ),
                path(
                    # Change the SRP payout amount
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/approve/"
                    ),
                    view=views.ajax_srp_request_approve,
                    name="ajax_srp_request_approve",
                ),
                path(
                    # Change the SRP payout amount
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/deny/"
                    ),
                    view=views.ajax_srp_request_deny,
                    name="ajax_srp_request_deny",
                ),
                path(
                    # Change the SRP payout amount
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/remove/"
                    ),
                    view=views.ajax_srp_request_remove,
                    name="ajax_srp_request_remove",
                ),
            ]
        ),
    ),
]
