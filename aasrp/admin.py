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
        "_creator",
        "srp_name",
        "srp_status",
        "fleet_doctrine",
        "fleet_time",
        "fleet_commander",
    )
    ordering = ("fleet_time",)

    list_filter = ("creator", "srp_status", "fleet_commander", "fleet_doctrine")

    @classmethod
    def _creator(cls, obj):
        return obj.creator.profile.main_character.character_name

    # _creator.short_description = "Creator"
    _creator.admin_order_field = "creator"


@admin.register(AaSrpRequest)
class AaSrpRequestAdmin(admin.ModelAdmin):
    list_display = (
        "request_code",
        "_creator",
        "character",
        "srp_link",
        "post_time",
        "ship_name",
        "loss_amount",
        "payout_amount",
        "killboard_link",
        "request_status",
    )
    ordering = ("post_time",)

    list_filter = ("creator", "character", "ship_name", "request_status")

    @classmethod
    def _creator(cls, obj):
        return obj.creator.profile.main_character.character_name

    # _creator.short_description = "Creator"
    _creator.admin_order_field = "creator"
