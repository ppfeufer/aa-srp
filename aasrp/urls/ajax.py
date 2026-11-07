"""
AA-SRP Ajax URLs

This module defines the URL patterns for the AJAX endpoints in the AA-SRP application. These endpoints
are used to handle asynchronous requests for managing SRP (Ship Replacement Program) links and requests.
Each URL pattern is associated with a specific view function that processes the corresponding AJAX request.
"""

# Django
from django.urls import path

# AA SRP
from aasrp.views import ajax
from aasrp.views.datatables import dashboard, own_srp_requests

urls = [
    path(
        "srp-link-data/active/",
        dashboard.DashboardSrpLinksView.as_view(),
        name="ajax_dashboard_srp_links_data",
    ),
    path(
        "srp-link-data/all/",
        dashboard.DashboardSrpLinksView.as_view(show_all_links=True),
        name="ajax_dashboard_srp_links_all_data",
    ),
    path(
        "user-srp-requests-data/",
        own_srp_requests.OwnSrpRequestsView.as_view(),
        name="ajax_own_srp_requests_data",
    ),
    path(
        "srp-link/<str:srp_code>/view-srp-requests-data/",
        ajax.srp_link_view_requests_data,
        name="ajax_srp_link_view_requests_data",
    ),
    path(
        "srp-link/<str:srp_code>/update-total-cost/",
        ajax.srp_link_update_total_cost,
        name="ajax_srp_link_update_total_cost",
    ),
    path(
        "srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/view-additional-information-data/",
        ajax.srp_request_additional_information,
        name="ajax_srp_request_additional_information",
    ),
    path(
        "srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/change-srp-payout/",
        ajax.srp_request_change_payout,
        name="ajax_srp_request_change_payout",
    ),
    path(
        "srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/approve/",
        ajax.srp_request_approve,
        name="ajax_srp_request_approve",
    ),
    path(
        "srp-link/<str:srp_code>/srp-request/approve/bulk/",
        ajax.srp_requests_bulk_approve,
        name="ajax_srp_requests_bulk_approve",
    ),
    path(
        "srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/deny/",
        ajax.srp_request_deny,
        name="ajax_srp_request_deny",
    ),
    path(
        "srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/open-character-info/",
        ajax.srp_request_open_character_info,
        name="ajax_srp_request_open_character_info",
    ),
    path(
        "srp-link/<str:srp_code>/srp-request/<str:srp_request_code>/remove/",
        ajax.srp_request_remove,
        name="ajax_srp_request_remove",
    ),
    path(
        "srp-link/<str:srp_code>/srp-request/remove/bulk/",
        ajax.srp_requests_bulk_remove,
        name="ajax_srp_requests_bulk_remove",
    ),
]
