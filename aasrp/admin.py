"""
Django admin declarations
"""

# Third Party
from solo.admin import SingletonModelAdmin

# Django
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

# AA SRP
from aasrp.form import SettingAdminForm
from aasrp.models import FleetType, RequestComment, Setting, SrpLink, SrpRequest


@admin.register(SrpLink)
class SrpLinkAdmin(admin.ModelAdmin):
    """
    SrpLinkAdmin
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
    @admin.display(description=_("Creator"), ordering="creator")
    def _creator(cls, obj):
        """
        Display the creator name

        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        return (
            obj.creator.profile.main_character.character_name
            if obj.creator.profile.main_character
            else obj.creator
        )


@admin.register(SrpRequest)
class SrpRequestAdmin(admin.ModelAdmin):
    """
    SrpRequestAdmin
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
    @admin.display(description=_("Requestor"), ordering="creator")
    def _creator(cls, obj):
        """
        Display the creator name

        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        return (
            obj.creator.profile.main_character.character_name
            if obj.creator.profile.main_character
            else obj.creator
        )


@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    """
    RequestCommentAdmin
    """

    list_display = ("srp_request", "comment_type", "creator")
    ordering = ("srp_request",)
    list_filter = ("comment_type",)


@admin.register(FleetType)
class FleetTypeAdmin(admin.ModelAdmin):
    """
    FleetTypeAdmin
    """

    list_display = ("id", "_name", "_is_enabled")
    list_filter = ("is_enabled",)
    ordering = ("name",)

    @admin.display(description=_("Fleet type"), ordering="name")
    def _name(self, obj):
        """
        Rewrite name

        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        return obj.name

    @admin.display(description=_("Is enabled"), boolean=True, ordering="is_enabled")
    def _is_enabled(self, obj):
        """
        Rewrite is_enabled

        :param obj:
        :type obj:
        :return:
        :rtype:
        """

        return obj.is_enabled

    actions = ("activate", "deactivate")

    @admin.action(description=_("Activate selected %(verbose_name_plural)s"))
    def activate(self, request, queryset):
        """
        Mark fleet type as active

        :param request:
        :type request:
        :param queryset:
        :type queryset:
        :return:
        :rtype:
        """

        notifications_count = 0
        failed = 0

        for obj in queryset:
            try:
                obj.is_enabled = True
                obj.save()

                notifications_count += 1
            except Exception:  # pylint: disable=broad-exception-caught
                failed += 1

        if failed:
            messages.error(
                request=request,
                message=ngettext(
                    singular="Failed to activate {failed} fleet type",
                    plural="Failed to activate {failed} fleet types",
                    number=failed,
                ).format(failed=failed),
            )

        if queryset.count() - failed > 0:
            messages.success(
                request=request,
                message=ngettext(
                    singular="Activated {notifications_count} fleet type",
                    plural="Activated {notifications_count} fleet types",
                    number=notifications_count,
                ).format(notifications_count=notifications_count),
            )

    @admin.action(description=_("Deactivate selected %(verbose_name_plural)s"))
    def deactivate(self, request, queryset):
        """
        Mark fleet type as inactive

        :param request:
        :type request:
        :param queryset:
        :type queryset:
        :return:
        :rtype:
        """

        # queryset.update(is_enabled=False)
        # self.message_user(request, f"{queryset.count()} releases disabled.")

        notifications_count = 0
        failed = 0

        for obj in queryset:
            try:
                obj.is_enabled = False
                obj.save()

                notifications_count += 1
            except Exception:  # pylint: disable=broad-exception-caught
                failed += 1

        if failed:
            messages.error(
                request=request,
                message=ngettext(
                    singular="Failed to deactivate {failed} fleet type",
                    plural="Failed to deactivate {failed} fleet types",
                    number=failed,
                ).format(failed=failed),
            )

        if queryset.count() - failed > 0:
            messages.success(
                request=request,
                message=ngettext(
                    singular="Deactivated {notifications_count} fleet type",
                    plural="Deactivated {notifications_count} fleet types",
                    number=notifications_count,
                ).format(notifications_count=notifications_count),
            )


@admin.register(Setting)
class SettingAdmin(SingletonModelAdmin):
    """
    Setting Admin
    """

    form = SettingAdminForm
