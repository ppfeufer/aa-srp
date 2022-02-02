"""
aasrp url config
"""

# Django
from django.urls import path

# AA SRP
from aasrp import views

app_name: str = "aasrp"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("all/", views.dashboard, {"show_all_links": True}, name="all"),
    path("add/", views.srp_link_add, name="add_srp_link"),
    path("srp-link/<str:srp_code>/edit/", views.srp_link_edit, name="edit_srp_link"),
    path(
        "srp-link/<str:srp_code>/view-srp-requests/",
        views.srp_link_view_requests,
        name="view_srp_requests",
    ),
    path(
        "srp-link/<str:srp_code>/enable/", views.enable_srp_link, name="enable_srp_link"
    ),
    path(
        "srp-link/<str:srp_code>/disable/",
        views.disable_srp_link,
        name="disable_srp_link",
    ),
    path(
        "srp-link/<str:srp_code>/delete/", views.delete_srp_link, name="delete_srp_link"
    ),
    path("srp-link/<str:srp_code>/request-srp/", views.request_srp, name="request_srp"),
    path(
        "srp-link/<str:srp_code>/complete/",
        views.complete_srp_link,
        name="complete_srp_link",
    ),
    # ajax calls
    path(
        # get active srp links
        "call/active-srp-links-data/",
        views.ajax_dashboard_srp_links_data,
        name="ajax_dashboard_srp_links_data",
    ),
    path(
        # get all srp links
        "call/active-srp-links-data/all/",
        views.ajax_dashboard_srp_links_data,
        {"show_all_links": True},
        name="ajax_dashboard_srp_links_all_data",
    ),
    path(
        # get all srp request for the current user
        "call/user-srp-requests-data/",
        views.ajax_dashboard_user_srp_requests_data,
        name="ajax_dashboard_user_srp_requests_data",
    ),
    path(
        # get all srp requests for the current srp link
        "call/srp-link/<str:srp_code>/view-srp-requests-data/",
        views.ajax_srp_link_view_requests_data,
        name="ajax_srp_link_view_requests_data",
    ),
    path(
        # get addition information for the current srp request
        (
            "call/srp-link/<str:srp_code>/srp-request/"
            "<str:srp_request_code>/view-additional-information-data/"
        ),
        views.ajax_srp_request_additional_information,
        name="ajax_srp_request_additional_information",
    ),
    path(
        # change the srp payout amount
        (
            "call/srp-link/<str:srp_code>/srp-request/"
            "<str:srp_request_code>/change-srp-payout/"
        ),
        views.ajax_srp_request_change_payout,
        name="ajax_srp_request_change_payout",
    ),
    path(
        # change the srp payout amount
        "call/srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/approve/",
        views.ajax_srp_request_approve,
        name="ajax_srp_request_approve",
    ),
    path(
        # change the srp payout amount
        "call/srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/deny/",
        views.ajax_srp_request_deny,
        name="ajax_srp_request_deny",
    ),
    path(
        # change the srp payout amount
        "call/srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/remove/",
        views.ajax_srp_request_remove,
        name="ajax_srp_request_remove",
    ),
]
