"""
AA-SRP Ajax URLs

This module defines the URL patterns for the AJAX endpoints in the AA-SRP application. These endpoints
are used to handle asynchronous requests for managing SRP (Ship Replacement Program) links and requests.
Each URL pattern is associated with a specific view function that processes the corresponding AJAX request.
"""

# Django
from django.urls import path

# AA SRP
from aasrp.views import ajax, datatables

urls = [
    path(
        "active-srp-links-data/",
        ajax.dashboard_srp_links_data,
        name="ajax_dashboard_srp_links_data",
    ),
    path(
        "active-srp-links-data/all/",
        ajax.dashboard_srp_links_data,
        {"show_all_links": True},
        name="ajax_dashboard_srp_links_all_data",
    ),
    path(
        "user-srp-requests-data/",
        datatables.OwnSrpRequestsView.as_view(),
        name="ajax_dashboard_user_srp_requests_data",
    ),
    path(
        "srp-link/<str:srp_code>/view-srp-requests-data/",
        ajax.srp_link_view_requests_data,
        name="ajax_srp_link_view_requests_data",
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
