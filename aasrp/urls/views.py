"""
AA-SRP Views URLs

This module defines the URL patterns for the AA-SRP application. Each URL pattern is associated
with a specific view function that handles the corresponding HTTP request. The views are imported
from the `aasrp.views.general` module.
"""

# Django
from django.urls import path

# AA SRP
from aasrp.views import general

urls = [
    # Route for viewing SRP links
    path(route="", view=general.srp_links, name="srp_links"),
    # Route for viewing all SRP links
    path(
        route="all/",
        view=general.srp_links,
        kwargs={"show_all_links": True},
        name="srp_links_all",
    ),
    # Route for viewing the user's own SRP requests
    path(
        route="my-srp-requests/",
        view=general.view_own_requests,
        name="own_srp_requests",
    ),
    # Route for managing user settings
    path(route="my-settings/", view=general.user_settings, name="user_settings"),
    # Route for adding a new SRP link
    path(route="add/", view=general.srp_link_add, name="add_srp_link"),
    # Route for editing an SRP link identified by its code
    path(
        route="srp-link/<str:srp_code>/edit/",
        view=general.srp_link_edit,
        name="edit_srp_link",
    ),
    # Route for viewing SRP requests associated with a specific SRP link
    path(
        route="srp-link/<str:srp_code>/view-srp-requests/",
        view=general.srp_link_view_requests,
        name="view_srp_requests",
    ),
    # Route for enabling an SRP link
    path(
        route="srp-link/<str:srp_code>/enable/",
        view=general.enable_srp_link,
        name="enable_srp_link",
    ),
    # Route for disabling an SRP link
    path(
        route="srp-link/<str:srp_code>/disable/",
        view=general.disable_srp_link,
        name="disable_srp_link",
    ),
    # Route for deleting an SRP link
    path(
        route="srp-link/<str:srp_code>/delete/",
        view=general.delete_srp_link,
        name="delete_srp_link",
    ),
    # Route for submitting an SRP request for a specific SRP link
    path(
        route="srp-link/<str:srp_code>/request-srp/",
        view=general.request_srp,
        name="request_srp",
    ),
    # Route for marking an SRP link as complete
    path(
        route="srp-link/<str:srp_code>/complete/",
        view=general.complete_srp_link,
        name="complete_srp_link",
    ),
]
