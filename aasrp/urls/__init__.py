"""
AA-SRP URL Configuration
"""

# Django
from django.urls import include, path

# AA SRP
from aasrp import __app_name__
from aasrp.constants import INTERNAL_URL_PREFIX
from aasrp.urls import ajax, views

app_name: str = __app_name__

urlpatterns = [
    # Views
    path(route="", view=include(views.urls)),
    # Ajax calls
    path(route=f"{INTERNAL_URL_PREFIX}/", view=include(ajax.urls)),
]
