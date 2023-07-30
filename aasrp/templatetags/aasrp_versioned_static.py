"""
Versioned static URLs to break browser caches when changing the app version
"""

# Django
from django.template.defaulttags import register
from django.templatetags.static import static

# AA SRP
from aasrp import __version__


@register.simple_tag
def aasrp_static(path: str) -> str:
    """
    Versioned static URL
    Adding the app version to any static file we load through this function.
    This is to make sure to break the browser cache on app updates.

    Example: /static/myapp/css/myapp.css?ver=1.0.0

    :param path:
    :type path:
    :return:
    :rtype:
    """

    static_url = static(path)
    versioned_url = static_url + "?v=" + __version__

    return versioned_url
