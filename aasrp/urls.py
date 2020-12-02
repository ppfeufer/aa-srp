# coding=utf-8

"""
aasrp url config
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
        views.ajax_dashboard_srp_links_data,
        name="ajax_dashboard_srp_links_data",
    ),
    url(
        r"^active-srp-links-data/all/$",
        views.ajax_dashboard_srp_links_data,
        {"show_all_links": True},
        name="ajax_dashboard_srp_links_all_data",
    ),
    url(
        r"^user-srp-requests-data/$",
        views.ajax_dashboard_user_srp_requests_data,
        name="ajax_dashboard_user_srp_requests_data",
    ),
    url(
        r"^srp-link/(\w+)/view-srp-requests-data/$",
        views.ajax_srp_link_view_requests_data,
        name="ajax_srp_link_view_requests_data",
    ),
    url(
        r"^srp-request/(\w+)/view-additional-information-data/$",
        views.ajax_srp_request_additional_information,
        name="ajax_srp_request_additional_information",
    ),
]
