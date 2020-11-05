# -*- coding: utf-8 -*-

"""
pages url config
"""

from django.urls import path

from aasrp import views


app_name: str = "aasrp"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
