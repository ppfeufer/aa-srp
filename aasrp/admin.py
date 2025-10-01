"""
Django admin declarations for the AA-SRP application.
This module defines the admin interface for managing SRP-related models.
"""

# Third Party
from solo.admin import SingletonModelAdmin

# Django
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

# Alliance Auth
from allianceauth.framework.api.user import get_main_character_name_from_user

# AA SRP
from aasrp.form import SettingAdminForm
from aasrp.helper.numbers import l10n_number_format
from aasrp.models import FleetType, RequestComment, Setting, SrpLink, SrpRequest


@admin.register(SrpLink)
class SrpLinkAdmin(admin.ModelAdmin):
    """
    Admin interface for managing SRP links.
    Provides options to view, filter, and search SRP links.
    """

    list_display = (
        "srp_code",
        "srp_name",
        "fleet_time",
        "_creator",
        "srp_status",
        "fleet_doctrine",
    )
    ordering = ("fleet_time",)
    list_filter = ("creator", "srp_status", "fleet_doctrine")
    search_fields = ("srp_code", "fleet_doctrine", "srp_name")

    @classmethod
    @admin.display(description=_("Creator"), ordering="creator")
    def _creator(cls, obj: SrpLink) -> str:
        """
        Display the name of the creator of the SRP link.

        :param obj: The SrpLink object.
        :type obj: SrpLink
        :return: The name of the creator.
        :rtype: str
        """

        return get_main_character_name_from_user(obj.creator)


@admin.register(SrpRequest)
class SrpRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for managing SRP requests.
    Provides options to view, filter, and search SRP requests.
    """

    list_display = (
        "request_code",
        "_requestor",
        "character",
        "srp_link",
        "_srp_code",
        "post_time",
        "ship_name",
        "_loss_amount",
        "_payout_amount",
        "killboard_link",
        "request_status",
    )
    ordering = ("post_time",)
    list_filter = ("creator", "character", "request_status")
    search_fields = (
        "request_code",
        "character__character_name",
        "ship_name",
        "srp_link__srp_name",
        "srp_link__srp_code",
    )

    @classmethod
    @admin.display(description=_("Requestor"), ordering="creator")
    def _requestor(cls, obj: SrpRequest) -> str:
        """
        Display the name of the requestor.

        :param obj: The SrpRequest object.
        :type obj: SrpRequest
        :return: The name of the requestor.
        :rtype: str
        """

        return get_main_character_name_from_user(obj.creator)

    @admin.display(description=_("SRP code"), ordering="srp_link__srp_code")
    def _srp_code(self, obj: SrpRequest) -> str:
        """
        Display the SRP code associated with the request.

        :param obj: The SrpRequest object.
        :type obj: SrpRequest
        :return: The SRP code.
        :rtype: str
        """

        return obj.srp_link.srp_code

    @admin.display(description=_("Loss amount"), ordering="loss_amount")
    def _loss_amount(self, obj: SrpRequest) -> str:
        """
        Display the loss amount for the SRP request.

        :param obj: The SrpRequest object.
        :type obj: SrpRequest
        :return: The loss amount formatted as a string.
        :rtype: str
        """

        localized_amount = l10n_number_format(obj.loss_amount, 2)

        return f"{localized_amount} ISK"

    @admin.display(description=_("Payout amount"), ordering="payout_amount")
    def _payout_amount(self, obj: SrpRequest) -> str:
        """
        Display the payout amount for the SRP request.

        :param obj: The SrpRequest object.
        :type obj: SrpRequest
        :return: The payout amount formatted as a string.
        :rtype: str
        """

        localized_amount = l10n_number_format(obj.payout_amount, 2)

        return f"{localized_amount} ISK"


@admin.register(RequestComment)
class RequestCommentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing comments on SRP requests.
    Provides options to view, filter, and search comments.
    """

    list_display = (
        "_request_code",
        "_srp_code",
        "_requestor",
        "_character",
        "comment_type",
    )
    ordering = ("srp_request",)
    list_filter = ("comment_type",)
    search_fields = (
        "srp_request__request_code",
        "srp_request__character__character_name",
        "srp_request__ship__name",
        "srp_request__srp_link__srp_code",
    )

    @admin.display(description=_("SRP code"), ordering="srp_request__srp_code")
    def _srp_code(self, obj: RequestComment) -> str:
        """
        Display the SRP code associated with the comment.

        :param obj: The RequestComment object.
        :type obj: RequestComment
        :return: The SRP code.
        :rtype: str
        """

        return obj.srp_request.srp_link.srp_code

    @admin.display(description=_("Request code"), ordering="srp_request__request_code")
    def _request_code(self, obj: RequestComment) -> str:
        """
        Display the request code associated with the comment.

        :param obj: The RequestComment object.
        :type obj: RequestComment
        :return: The request code.
        :rtype: str
        """

        return obj.srp_request.request_code

    @admin.display(description=_("Requestor"), ordering="srp_request__creator")
    def _requestor(self, obj: RequestComment) -> str:
        """
        Display the name of the requestor associated with the comment.

        :param obj: The RequestComment object.
        :type obj: RequestComment
        :return: The name of the requestor.
        :rtype: str
        """

        return get_main_character_name_from_user(obj.srp_request.creator)

    @admin.display(description=_("Character"), ordering="srp_request__character")
    def _character(self, obj: RequestComment) -> str:
        """
        Display the name of the character associated with the request.

        :param obj: The RequestComment object.
        :type obj: RequestComment
        :return: The character name.
        :rtype: str
        """

        return obj.srp_request.character.character_name


@admin.register(FleetType)
class FleetTypeAdmin(admin.ModelAdmin):
    """
    Admin interface for managing fleet types.
    Provides options to activate or deactivate fleet types.
    """

    list_display = ("name", "is_enabled")
    list_filter = ("is_enabled",)
    ordering = ("name",)
    search_fields = ("name",)
    actions = ("activate", "deactivate")

    @admin.action(description=_("Activate selected %(verbose_name_plural)s"))
    def activate(self, request: HttpRequest, queryset: QuerySet[FleetType]) -> None:
        """
        Activate the selected fleet types.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of FleetType objects to activate.
        :type queryset: QuerySet[FleetType]
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
    def deactivate(self, request: HttpRequest, queryset: QuerySet[FleetType]) -> None:
        """
        Deactivate the selected fleet types.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :param queryset: The queryset of FleetType objects to deactivate.
        :type queryset: QuerySet[FleetType]
        """

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
    Admin interface for managing application settings.
    Uses a singleton model to ensure only one instance of settings exists.
    """

    form = SettingAdminForm
