"""
AA-SRP Ajax URLs

This module defines the URL patterns for the AJAX endpoints in the AA-SRP application. These endpoints
are used to handle asynchronous requests for managing SRP (Ship Replacement Program) links and requests.
Each URL pattern is associated with a specific view function that processes the corresponding AJAX request.
"""

# Django
from django.urls import include, path

# AA SRP
from aasrp.views import ajax

urls = [
    path(
        route="ajax/",
        view=include(
            [
                path(
                    # Get active SRP links
                    route="active-srp-links-data/",
                    view=ajax.dashboard_srp_links_data,
                    name="ajax_dashboard_srp_links_data",
                ),
                path(
                    # Get all SRP links
                    route="active-srp-links-data/all/",
                    view=ajax.dashboard_srp_links_data,
                    kwargs={"show_all_links": True},
                    name="ajax_dashboard_srp_links_all_data",
                ),
                path(
                    # Get all SRP requests for the current user
                    route="user-srp-requests-data/",
                    view=ajax.dashboard_user_srp_requests_data,
                    name="ajax_dashboard_user_srp_requests_data",
                ),
                path(
                    # Get all SRP requests for the current SRP link
                    route="srp-link/<str:srp_code>/view-srp-requests-data/",
                    view=ajax.srp_link_view_requests_data,
                    name="ajax_srp_link_view_requests_data",
                ),
                path(
                    # Get additional information for the current SRP request
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/view-additional-information-data/"
                    ),
                    view=ajax.srp_request_additional_information,
                    name="ajax_srp_request_additional_information",
                ),
                path(
                    # Change the SRP payout amount
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/change-srp-payout/"
                    ),
                    view=ajax.srp_request_change_payout,
                    name="ajax_srp_request_change_payout",
                ),
                path(
                    # Approve the SRP request
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/approve/"
                    ),
                    view=ajax.srp_request_approve,
                    name="ajax_srp_request_approve",
                ),
                path(
                    # Bulk approve SRP requests
                    route=("srp-link/<str:srp_code>/srp-request/approve/bulk/"),
                    view=ajax.srp_requests_bulk_approve,
                    name="ajax_srp_requests_bulk_approve",
                ),
                path(
                    # Deny the SRP request
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/deny/"
                    ),
                    view=ajax.srp_request_deny,
                    name="ajax_srp_request_deny",
                ),
                path(
                    # Remove the SRP request
                    route=(
                        "srp-link/<str:srp_code>/srp-request/"
                        "<str:srp_request_code>/remove/"
                    ),
                    view=ajax.srp_request_remove,
                    name="ajax_srp_request_remove",
                ),
                path(
                    # Bulk remove SRP requests
                    route=("srp-link/<str:srp_code>/srp-request/remove/bulk/"),
                    view=ajax.srp_requests_bulk_remove,
                    name="ajax_srp_requests_bulk_remove",
                ),
            ]
        ),
    ),
]
