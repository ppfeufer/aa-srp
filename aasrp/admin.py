# coding=utf-8

"""
Django admin declarations
"""

from aasrp.models import AaSrpLink, AaSrpRequest, AaSrpRequestComment

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
    """
    AaSrpLinkAdmin
    """

    list_display = (
        "srp_code",
        "fleet_time",
        "_creator",
        "srp_name",
        "srp_status",
        "fleet_doctrine",
    )
    ordering = ("fleet_time",)

    list_filter = ("creator", "srp_status", "fleet_doctrine")

    search_fields = ("srp_code", "fleet_doctrine", "srp_name")

    @classmethod
    def _creator(cls, obj):
        creator_name = obj.creator
        if obj.creator.profile.main_character:
            creator_name = obj.creator.profile.main_character.character_name

        return creator_name

    _creator.short_description = "Creator"
    _creator.admin_order_field = "creator"


@admin.register(AaSrpRequest)
class AaSrpRequestAdmin(admin.ModelAdmin):
    """
    AaSrpRequestAdmin
    """

    list_display = (
        "request_code",
        "_creator",
        "character",
        "srp_link",
        "post_time",
        "ship",
        "loss_amount",
        "payout_amount",
        "killboard_link",
        "request_status",
    )
    ordering = ("post_time",)

    list_filter = ("creator", "character", "request_status")

    search_fields = (
        "request_code",
        "character__character_name",
        "ship__name",
        "srp_link__srp_code",
    )

    @classmethod
    def _creator(cls, obj):
        creator_name = obj.creator
        if obj.creator.profile.main_character:
            creator_name = obj.creator.profile.main_character.character_name

        return creator_name

    _creator.short_description = "Creator"
    _creator.admin_order_field = "creator"


@admin.register(AaSrpRequestComment)
class AaSrpRequestCommentAdmin(admin.ModelAdmin):
    """
    AaSrpRequestCommentAdmin
    """

    list_display = ("id", "comment_type", "creator")
    ordering = ("id",)
