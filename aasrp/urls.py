# -*- coding: utf-8 -*-

"""
pages url config
"""

from django.conf.urls import url

from aasrp import views


app_name: str = "aasrp"

urlpatterns = [
    url(r"^$", views.dashboard, name="dashboard"),
    url(r"^all/$", views.dashboard, {"show_all_links": True}, name="all"),
    url(r"^add/$", views.srp_link_add, name="add_srp_link"),
    url(r"^srp-link/(\w+)/edit/$", views.srp_link_edit, name="edit_srp_link"),
    url(
        r"^srp-link/(\w+)/view-srp-requests/$",
        views.srp_link_view_requests,
        name="view_srp_requests",
    ),
    url(r"^srp-link/(\w+)/enable/$", views.enable_srp_link, name="enable_srp_link"),
    url(r"^srp-link/(\w+)/disable/$", views.disable_srp_link, name="disable_srp_link"),
    url(r"^srp-link/(\w+)/delete/$", views.delete_srp_link, name="delete_srp_link"),
    url(r"^srp-link/(\w+)/request-srp/$", views.request_srp, name="request_srp"),
    # ajax calls
    url(
        r"^active-srp-links-data/$",
        views.active_srp_links_data,
        name="active_srp_links_data",
    ),
    url(
        r"^active-srp-links-data/all/$",
        views.active_srp_links_data,
        {"show_all_links": True},
        name="active_srp_links_all_data",
    ),
    url(
        r"^user-srp-requests-data/$",
        views.user_srp_requests_data,
        name="user_srp_requests_data",
    ),
    url(
        r"^srp-link/(\w+)/view-srp-requests-data/$",
        views.srp_link_view_requests_data,
        name="srp_link_view_requests_data",
    ),
]
