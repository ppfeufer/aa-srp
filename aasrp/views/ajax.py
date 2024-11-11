"""
Ajax views
"""

# Django
from django.contrib.auth.decorators import login_required, permission_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.authentication.decorators import permissions_required
from allianceauth.framework.api.user import get_main_character_name_from_user
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag
from app_utils.urls import reverse_absolute
from eveuniverse.models import EveType

# AA SRP
from aasrp import __title__
from aasrp.constants import SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE
from aasrp.discord.direct_message import send_user_notification
from aasrp.form import (
    SrpRequestAcceptForm,
    SrpRequestAcceptRejectedForm,
    SrpRequestPayoutForm,
    SrpRequestRejectForm,
)
from aasrp.helper.character import get_formatted_character_name
from aasrp.helper.eve_images import get_type_render_url_from_type_id
from aasrp.helper.icons import (
    get_dashboard_action_icons,
    get_srp_request_action_icons,
    get_srp_request_details_icon,
    get_srp_request_status_icon,
)
from aasrp.helper.user import get_user_settings
from aasrp.managers import SrpManager
from aasrp.models import RequestComment, SrpLink, SrpRequest

logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


def _attempt_to_re_add_ship_information_to_request(
    srp_request: SrpRequest,
) -> SrpRequest:
    """
    If for some reason the ship gets removed from EveType table,
    srp_request.ship is None. In this case, we have to re-add the ship to prevent
    errors in our DataTables ...

    :param srp_request:
    :type srp_request:
    :return:
    :rtype:
    """

    srp_kill_link_id = SrpManager.get_kill_id(killboard_link=srp_request.killboard_link)

    (
        ship_type_id,
        ship_value,  # pylint: disable=unused-variable
        victim_id,  # pylint: disable=unused-variable
    ) = SrpManager.get_kill_data(kill_id=srp_kill_link_id)
    (
        srp_request__ship,
        created_from_esi,  # pylint: disable=unused-variable
    ) = EveType.objects.get_or_create_esi(id=ship_type_id)

    srp_request.ship_name = srp_request__ship.name
    srp_request.ship = srp_request__ship
    srp_request.save()

    return srp_request


@login_required
@permission_required("aasrp.basic_access")
def dashboard_srp_links_data(
    request: WSGIRequest, show_all_links: bool = False
) -> JsonResponse:
    """
    Ajax request :: Get all active SRP links

    :param request:
    :type request:
    :param show_all_links:
    :type show_all_links:
    :return:
    :rtype:
    """

    data = []

    srp_links = SrpLink.objects.prefetch_related(
        "fleet_commander",
        "creator",
        "creator__profile__main_character",
        "srp_requests",
    ).all()

    if not show_all_links:
        srp_links = srp_links.filter(srp_status=SrpLink.Status.ACTIVE)

    for srp_link in srp_links:
        aar_link = ""
        if srp_link.aar_link:
            aar_href = srp_link.aar_link
            link_text = _("Link")
            aar_link = f'<a href="{aar_href}" target="_blank">{link_text}</a>'

        srp_code_html = srp_link.srp_code
        if srp_link.srp_status == SrpLink.Status.ACTIVE:
            css_classes = "aa-srp-fa-icon copy-text-fa-icon fa-regular fa-copy ms-2"
            srp_link_href = reverse_absolute(
                viewname="aasrp:request_srp", args=[srp_link.srp_code]
            )
            title = _("Copy SRP link to clipboard")
            srp_code_html += (
                f'<i class="{css_classes}" '
                f'data-clipboard-text="{srp_link_href}" title="{title}" '
                'data-bs-tooltip="aa-srp"></i>'
            )

        actions = get_dashboard_action_icons(request=request, srp_link=srp_link)

        fleet_type = ""
        if srp_link.fleet_type:
            fleet_type = srp_link.fleet_type.name

        data.append(
            {
                "srp_name": srp_link.srp_name,
                "creator": get_main_character_name_from_user(user=srp_link.creator),
                "fleet_time": srp_link.fleet_time,
                "fleet_type": fleet_type,
                # "fleet_commander": srp_link.fleet_commander.character_name,
                "fleet_doctrine": srp_link.fleet_doctrine,
                "aar_link": aar_link,
                "srp_code": {"display": srp_code_html, "sort": srp_link.srp_code},
                "srp_costs": srp_link.total_cost,
                "srp_status": srp_link.srp_status,
                "pending_requests": srp_link.pending_requests,
                "actions": actions,
            }
        )

    return JsonResponse(data=data, safe=False)


@login_required
@permission_required("aasrp.basic_access")
def dashboard_user_srp_requests_data(request: WSGIRequest) -> JsonResponse:
    """
    Ajax request :: Get user srp requests

    :param request:
    :type request:
    :return:
    :rtype:
    """

    data = []

    requests = (
        SrpRequest.objects.filter(creator=request.user)
        # .filter(ship__isnull=False)
        .prefetch_related(
            "creator",
            "creator__profile__main_character",
            "character",
            "srp_link",
            "srp_link__creator",
            "srp_link__creator__profile__main_character",
            "ship",
        )
    )

    for srp_request in requests:
        killboard_link = ""

        if srp_request.killboard_link:
            try:
                ship_render_icon_html = get_type_render_url_from_type_id(
                    evetype_id=srp_request.ship_id,
                    evetype_name=srp_request.ship.name,
                    size=32,
                    as_html=True,
                )
            except AttributeError:
                # For some reason, it seems the ship has been removed from EveType
                # table, attempt to add it again ...
                srp_request = _attempt_to_re_add_ship_information_to_request(
                    srp_request=srp_request
                )

                ship_render_icon_html = get_type_render_url_from_type_id(
                    evetype_id=srp_request.ship_id,
                    evetype_name=srp_request.ship.name,
                    size=32,
                    as_html=True,
                )

            zkb_link = srp_request.killboard_link
            zkb_link_text = srp_request.ship.name
            killboard_link = (
                f'<a href="{zkb_link}" target="_blank">'
                f"{ship_render_icon_html}"
                f"<span>{zkb_link_text}</span>"
                "</a>"
            )

        srp_request_status_icon = get_srp_request_status_icon(
            request=request, srp_request=srp_request
        )

        srp_request_details_icon = get_srp_request_details_icon(
            request=request, srp_link=srp_request.srp_link, srp_request=srp_request
        )

        character_display = get_formatted_character_name(
            character=srp_request.character, with_portrait=True
        )
        character_sort = get_formatted_character_name(character=srp_request.character)

        data.append(
            {
                "request_time": srp_request.post_time,
                "character_html": {
                    "display": character_display,
                    "sort": character_sort,
                },
                "character": srp_request.character.character_name,
                "fleet_name": srp_request.srp_link.srp_name,
                "srp_code": srp_request.srp_link.srp_code,
                "request_code": srp_request.request_code,
                "ship_html": {
                    "display": killboard_link,
                    "sort": srp_request.ship.name,
                },
                "ship": srp_request.ship.name,
                "zkb_link": killboard_link,
                "zbk_loss_amount": srp_request.loss_amount,
                "payout_amount": srp_request.payout_amount,
                "request_status_icon": (
                    srp_request_details_icon + srp_request_status_icon
                ),
                "request_status": srp_request.get_request_status_display(),
            }
        )

    return JsonResponse(data=data, safe=False)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_link_view_requests_data(request: WSGIRequest, srp_code: str) -> JsonResponse:
    """
    Ajax request :: Get datatable data

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :return:
    :rtype:
    """

    data = []

    srp_requests = SrpRequest.objects.filter(
        srp_link__srp_code__iexact=srp_code
    ).prefetch_related(
        "srp_link",
        "srp_link__creator",
        "srp_link__creator__profile__main_character",
        "character",
        "ship",
    )

    for srp_request in srp_requests:
        killboard_link = ""
        if srp_request.killboard_link:
            try:
                ship_render_icon_html = get_type_render_url_from_type_id(
                    evetype_id=srp_request.ship_id,
                    evetype_name=srp_request.ship.name,
                    size=32,
                    as_html=True,
                )
            except AttributeError:
                # For some reason, it seems the ship has been removed from EveType
                # table, attempt to add it again ...
                srp_request = _attempt_to_re_add_ship_information_to_request(
                    srp_request
                )

                ship_render_icon_html = get_type_render_url_from_type_id(
                    evetype_id=srp_request.ship_id,
                    evetype_name=srp_request.ship.name,
                    size=32,
                    as_html=True,
                )

            killboard_link = (
                f'<a href="{srp_request.killboard_link}" target="_blank">'
                f"{ship_render_icon_html}"
                f"<span>{srp_request.ship.name}</span></a>"
            )

        srp_request_status_icon = get_srp_request_status_icon(
            request=request, srp_request=srp_request
        )
        srp_request_action_icons = get_srp_request_action_icons(
            request=request, srp_link=srp_request.srp_link, srp_request=srp_request
        )
        character_display = get_formatted_character_name(
            character=srp_request.character, with_portrait=True, with_copy_icon=True
        )
        character_sort = get_formatted_character_name(character=srp_request.character)

        data.append(
            {
                "request_time": srp_request.post_time,
                "requester": get_main_character_name_from_user(srp_request.creator),
                "character_html": {
                    "display": character_display,
                    "sort": character_sort,
                },
                "character": srp_request.character.character_name,
                "request_code": srp_request.request_code,
                "srp_code": srp_request.srp_link.srp_code,
                "ship_html": {"display": killboard_link, "sort": srp_request.ship.name},
                "ship": srp_request.ship.name,
                "zkb_link": killboard_link,
                "zbk_loss_amount": srp_request.loss_amount,
                "payout_amount": srp_request.payout_amount,
                "request_status_icon": srp_request_status_icon,
                "actions": srp_request_action_icons,
                "request_status_translated": srp_request.get_request_status_display(),
                "request_status": srp_request.request_status,
            }
        )

    return JsonResponse(data, safe=False)


@login_required
@permission_required("aasrp.basic_access")
def srp_request_additional_information(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> HttpResponse:
    """
    Ajax Call :: Get additional information for an SRP request

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :param srp_request_code:
    :type srp_request_code:
    :return:
    :rtype:
    """

    srp_request = SrpRequest.objects.get(
        srp_link__srp_code=srp_code, request_code=srp_request_code
    )

    insurance_information = srp_request.insurance.filter(srp_request=srp_request)

    character = get_formatted_character_name(
        character=srp_request.character, with_portrait=True
    )

    try:
        ship_render_icon_html = get_type_render_url_from_type_id(
            evetype_id=srp_request.ship_id,
            evetype_name=srp_request.ship.name,
            size=32,
            as_html=True,
        )
    except AttributeError:
        # For some reason, it seems the ship has been removed from EveType
        # table, attempt to add it again ...
        srp_request = _attempt_to_re_add_ship_information_to_request(
            srp_request=srp_request
        )

        ship_render_icon_html = get_type_render_url_from_type_id(
            evetype_id=srp_request.ship_id,
            evetype_name=srp_request.ship.name,
            size=32,
            as_html=True,
        )

    request_status_banner_alert_level = "info"
    if srp_request.request_status == SrpRequest.Status.APPROVED:
        request_status_banner_alert_level = "success"

    if srp_request.request_status == SrpRequest.Status.REJECTED:
        request_status_banner_alert_level = "danger"

    try:
        additional_info_comment = RequestComment.objects.get(
            srp_request=srp_request, comment_type=RequestComment.Type.REQUEST_INFO
        )

        additional_info = additional_info_comment.comment
    except RequestComment.DoesNotExist:
        additional_info = ""

    try:
        request_history = RequestComment.objects.filter(
            ~Q(comment_type=RequestComment.Type.REQUEST_INFO),
            srp_request=srp_request,
        ).order_by("pk")
    except RequestComment.DoesNotExist:
        request_history = ""

    data = {
        "srp_request": srp_request,
        "ship_render_icon_html": ship_render_icon_html,
        "ship_type": srp_request.ship.name,
        "requester": get_main_character_name_from_user(user=srp_request.creator),
        "character": character,
        "additional_info": additional_info,
        "request_status_banner_alert_level": request_status_banner_alert_level,
        "request_status": srp_request.get_request_status_display(),
        "insurance_information": insurance_information,
        "request_history": request_history,
    }

    return render(
        request=request,
        template_name="aasrp/ajax-render/srp-request-additional-information.html",
        context=data,
    )


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_request_change_payout(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Ajax call :: Change SRP payout

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :param srp_request_code:
    :type srp_request_code:
    :return:
    :rtype:
    """

    data = []

    if request.method == "POST":
        try:
            srp_request = SrpRequest.objects.get(
                request_code=srp_request_code, srp_link__srp_code=srp_code
            )
        except SrpRequest.DoesNotExist:
            data.append({"success": False})
        else:
            # check whether it's valid:
            form = SrpRequestPayoutForm(data=request.POST)
            if form.is_valid():
                srp_payout = form.cleaned_data["value"]

                srp_request.payout_amount = srp_payout
                srp_request.save()

                data.append({"success": True})
            else:
                data.append({"success": False})

    return JsonResponse(data=data, safe=False)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_request_approve(  # pylint: disable=too-many-locals
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Ajax call :: Approve SRP request

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :param srp_request_code:
    :type srp_request_code:
    :return:
    :rtype:
    """

    data = []

    try:
        srp_request = SrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )
    except SrpRequest.DoesNotExist:
        data.append({"success": False})
    else:
        if request.method == "POST":
            # Create a form instance and populate it with data from the request
            form = None

            if srp_request.request_status == SrpRequest.Status.PENDING:
                form = SrpRequestAcceptForm(data=request.POST)
            elif srp_request.request_status == SrpRequest.Status.REJECTED:
                form = SrpRequestAcceptRejectedForm(data=request.POST)

            if form and form.is_valid():
                requester = srp_request.creator
                srp_payout = srp_request.payout_amount
                srp_isk_loss = srp_request.loss_amount

                # Reviser comment
                reviser_comment = form.cleaned_data["comment"]

                if srp_payout == 0:
                    srp_request.payout_amount = srp_isk_loss

                # Set new status in request history
                RequestComment(
                    srp_request=srp_request,
                    comment_type=RequestComment.Type.STATUS_CHANGE,
                    new_status=SrpRequest.Status.APPROVED,
                    creator=request.user,
                ).save()

                # Save reviser comment
                if reviser_comment != "":
                    RequestComment(
                        srp_request=srp_request,
                        comment=reviser_comment,
                        comment_type=RequestComment.Type.REVISER_COMMENT,
                        creator=request.user,
                    ).save()

                srp_request.request_status = SrpRequest.Status.APPROVED
                srp_request.save()

                requester_user_settings = get_user_settings(user=requester)

                # Check if the requester has notifications activated (it's by default)
                if requester_user_settings.disable_notifications is False:
                    ship_name = srp_request.ship.name
                    fleet_name = srp_request.srp_link.srp_name
                    srp_code = srp_request.srp_link.srp_code
                    request_code = srp_request.request_code
                    reviser = get_main_character_name_from_user(user=request.user)
                    reviser_comment = (
                        f"\nComment:\n{reviser_comment}\n"
                        if reviser_comment != ""
                        else ""
                    )
                    inquiry_note = SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE
                    notification_message = (
                        f"Your SRP request regarding your {ship_name} lost during "
                        f"{fleet_name} has been approved.\n\n"
                        f"Request Details:\nSRP Code: {srp_code}\n"
                        f"Request Code: {request_code}\n"
                        f"Reviser: {reviser}\n{reviser_comment}\n{inquiry_note}"
                    )

                    logger.info(msg="Sending approval message to user")

                    send_user_notification(
                        user=requester,
                        level="success",
                        title="SRP Request Approved",
                        message=notification_message,
                    )

                data.append(
                    {"success": True, "message": _("SRP request has been approved")}
                )

    return JsonResponse(data=data, safe=False)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_request_deny(
    request: WSGIRequest, srp_code: str, srp_request_code: str
) -> JsonResponse:
    """
    Ajax call :: Deny SRP request

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :param srp_request_code:
    :type srp_request_code:
    :return:
    :rtype:
    """

    data = []

    try:
        srp_request = SrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )
    except SrpRequest.DoesNotExist:
        data.append({"success": False})
    else:
        if request.method == "POST":
            # Create a form instance and populate it with data from the request
            form = SrpRequestRejectForm(data=request.POST)

            # Check whether it's valid:
            if form.is_valid():
                reject_info = form.cleaned_data["comment"]
                requester = srp_request.creator

                srp_request.payout_amount = 0
                srp_request.request_status = SrpRequest.Status.REJECTED
                srp_request.save()

                # Set new status in request history
                RequestComment(
                    srp_request=srp_request,
                    comment_type=RequestComment.Type.STATUS_CHANGE,
                    new_status=SrpRequest.Status.REJECTED,
                    creator=request.user,
                ).save()

                # Save reject reason as comment for this request
                RequestComment(
                    comment=reject_info,
                    srp_request=srp_request,
                    comment_type=RequestComment.Type.REJECT_REASON,
                    creator=request.user,
                ).save()

                requester_user_settings = get_user_settings(user=requester)

                # Check if the requester has notifications activated (it's by default)
                if requester_user_settings.disable_notifications is False:
                    ship_name = srp_request.ship.name
                    fleet_name = srp_request.srp_link.srp_name
                    srp_code = srp_request.srp_link.srp_code
                    request_code = srp_request.request_code
                    reviser = get_main_character_name_from_user(user=request.user)
                    inquiry_note = SRP_REQUEST_NOTIFICATION_INQUIRY_NOTE
                    notification_message = (
                        f"Your SRP request regarding your {ship_name} lost during "
                        f"{fleet_name} has been rejected.\n\n"
                        f"Reason:\n{reject_info}\n\n"
                        f"Request Details:\nSRP Code: {srp_code}\n"
                        f"Request Code: {request_code}\n"
                        f"Reviser: {reviser}\n\n{inquiry_note}"
                    )

                    logger.info(msg="Sending reject message to user")

                    send_user_notification(
                        user=requester,
                        level="danger",
                        title=_("SRP request rejected"),
                        message=notification_message,
                    )

                data.append(
                    {"success": True, "message": _("SRP request has been rejected")}
                )

    return JsonResponse(data=data, safe=False)


@login_required
@permissions_required(("aasrp.manage_srp", "aasrp.manage_srp_requests"))
def srp_request_remove(
    request: WSGIRequest,  # pylint: disable=unused-argument
    srp_code: str,
    srp_request_code: str,
) -> JsonResponse:
    """
    Ajax call :: Remove SRP request

    :param request:
    :type request:
    :param srp_code:
    :type srp_code:
    :param srp_request_code:
    :type srp_request_code:
    :return:
    :rtype:
    """

    data = []

    try:
        srp_request = SrpRequest.objects.get(
            request_code=srp_request_code, srp_link__srp_code=srp_code
        )
    except SrpRequest.DoesNotExist:
        data.append({"success": False})
    else:
        srp_request.delete()

        data.append({"success": True, "message": _("SRP request has been removed")})

    return JsonResponse(data=data, safe=False)
