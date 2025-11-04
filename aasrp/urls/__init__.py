"""
AA-SRP URL Configuration

This module defines the URL configuration for the AA-SRP application. It includes the URL patterns
for both the views and AJAX endpoints. The `urlpatterns` list is used by Django to route HTTP requests
to the appropriate view functions.

Attributes:
    app_name (str): The name of the application, used for namespacing URLs.
    urlpatterns (list): A list of URL patterns for the application, including views and AJAX endpoints.
"""

# Django
from django.urls import include, path

# AA SRP
from aasrp import __app_name__
from aasrp.constants import INTERNAL_URL_PREFIX
from aasrp.urls import ajax, views

app_name: str = __app_name__  # pylint: disable=invalid-name

urlpatterns = [
    # Include the URL patterns for the views
    path(route="", view=include(views.urls)),
    # Include the URL patterns for the AJAX endpoints, prefixed with the internal URL prefix
    path(route=f"{INTERNAL_URL_PREFIX}/", view=include(ajax.urls)),
]
