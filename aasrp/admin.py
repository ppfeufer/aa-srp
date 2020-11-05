# coding=utf-8

"""
Django admin declarations
"""

from aasrp.models import AaSrpLink, AaSrpRequest

from django.contrib import admin


def custom_filter(title):
    """
    custom filter for model properties
    :param title:
    :return:
    """

    class Wrapper(admin.FieldListFilter):
        """
        custom_filter :: wrapper
        """

        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title

            return instance

    return Wrapper


@admin.register(AaSrpLink)
class AaSrpLinkAdmin(admin.ModelAdmin):
    list_display = (
        "srp_code",
        "srp_name",
        "srp_status",
        "fleet_doctrine",
        "fleet_time",
        "fleet_commander",
    )
    ordering = ("fleet_time",)
    # list_filter = ("is_enabled",)


@admin.register(AaSrpRequest)
class AaSrpRequestAdmin(admin.ModelAdmin):
    list_display = (
        "request_code",
        "srp_link",
        "post_time",
        "character",
        "ship_name",
        "loss_amount",
        "payout_amount",
        "killboard_link",
        "request_status",
    )
    ordering = ("post_time",)
