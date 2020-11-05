# -*- coding: utf-8 -*-

"""
the views
"""

import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required

from aasrp.app_settings import avoid_cdn


@login_required
@permission_required("aasrp.basic_access")
def dashboard(request):
    """
    Index view
    """

    context = {
        "avoidCdn": avoid_cdn(),
    }

    return render(request, "aasrp/dashboard.html", context)
