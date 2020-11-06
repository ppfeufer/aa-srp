# -*- coding: utf-8 -*-

"""
pages url config
"""

from django.conf.urls import url

from aasrp import views


app_name: str = "aasrp"

urlpatterns = [
    url(r"^$", views.dashboard, name="dashboard"),
    url(r"^all/$", views.dashboard, {"all": True}, name="all"),
    url(r"^add/$", views.srp_link_add, name="add_srp_link"),
    # ajax calls
    url(
        r"^active_srp_links_data/$",
        views.active_srp_links_data,
        name="active_srp_links_data",
    ),
    url(
        r"^pending_user_srp_requests_data/$",
        views.pending_user_srp_requests_data,
        name="pending_user_srp_requests_data",
    ),
]
