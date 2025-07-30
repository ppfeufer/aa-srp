"""
AA-SRP Views URLs
"""

# Django
from django.urls import path

# AA SRP
from aasrp.views import general

urls = [
    path(route="", view=general.srp_links, name="srp_links"),
    path(
        route="all/",
        view=general.srp_links,
        kwargs={"show_all_links": True},
        name="srp_links_all",
    ),
    path(
        route="my-srp-requests/",
        view=general.view_own_requests,
        name="own_srp_requests",
    ),
    path(route="my-settings/", view=general.user_settings, name="user_settings"),
    path(route="add/", view=general.srp_link_add, name="add_srp_link"),
    path(
        route="srp-link/<str:srp_code>/edit/",
        view=general.srp_link_edit,
        name="edit_srp_link",
    ),
    path(
        route="srp-link/<str:srp_code>/view-srp-requests/",
        view=general.srp_link_view_requests,
        name="view_srp_requests",
    ),
    path(
        route="srp-link/<str:srp_code>/enable/",
        view=general.enable_srp_link,
        name="enable_srp_link",
    ),
    path(
        route="srp-link/<str:srp_code>/disable/",
        view=general.disable_srp_link,
        name="disable_srp_link",
    ),
    path(
        route="srp-link/<str:srp_code>/delete/",
        view=general.delete_srp_link,
        name="delete_srp_link",
    ),
    path(
        route="srp-link/<str:srp_code>/request-srp/",
        view=general.request_srp,
        name="request_srp",
    ),
    path(
        route="srp-link/<str:srp_code>/complete/",
        view=general.complete_srp_link,
        name="complete_srp_link",
    ),
]
