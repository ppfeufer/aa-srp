"""
Datatables view for SRP requests.
"""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.db.models.query import Prefetch
from django.http.request import HttpRequest

# Alliance Auth
from allianceauth.framework.datatables import DataTablesView
from allianceauth.services.hooks import get_extension_logger

# AA SRP
from aasrp.models import RequestComment, SrpRequest
from aasrp.providers.applogger import AppLogger

logger = AppLogger(my_logger=get_extension_logger(name=__name__))


class SrpRequestsView(PermissionRequiredMixin, DataTablesView):
    """
    Datatables view for SRP requests.
    """

    # Either permission is sufficient to view the datatable
    permission_required = ("aasrp.manage_srp", "aasrp.manage_srp_requests")
    model = SrpRequest

    visible_columns = [
        ("post_time", "{{ row.post_time.isoformat }}"),
        (
            "creator__profile__main_character__character_name",
            "aasrp/partials/datatables/view-requests/column-requestor.html",
        ),
        (
            "character__character_name",
            "aasrp/partials/datatables/view-requests/column-character.html",
        ),
        (
            "ship__ship_name",
            "aasrp/partials/datatables/view-requests/column-ship.html",
        ),
        (
            "loss_amount",
            "aasrp/partials/datatables/view-requests/column-isk-lost.html",
        ),
        (
            "payout_amount",
            "{{ row.payout_amount }}",
        ),
        (
            "srp_request_comments__comment",
            "aasrp/partials/datatables/view-requests/column-additional-information.html",
        ),
        (
            "request_status",
            "aasrp/partials/datatables/view-requests/column-status.html",
        ),
        ("", "aasrp/partials/datatables/view-requests/column-actions.html"),
        ("", "aasrp/partials/datatables/view-requests/column-bulk-actions.html"),
    ]
    invisible_columns = [
        (
            "request_code",
            "aasrp/partials/datatables/view-requests/column-request-code.html",
        ),
        ("request_status", "{{ row.request_status }}"),
    ]
    columns = visible_columns + invisible_columns

    def has_permission(self):
        """
        Check if the user has any of the required permissions.

        :return: True if the user has any of the required permissions, False otherwise.
        :rtype: bool
        """

        perms = self.get_permission_required()
        user = self.request.user

        if isinstance(perms, str):
            return user.has_perm(perms)

        return any(user.has_perm(p) for p in perms)

    def get_model_qs(  # pylint: disable=unused-argument
        self,
        request: HttpRequest,
        *args,
        srp_code=None,
        **kwargs,
    ) -> QuerySet:
        """
        Get the queryset for the model.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :param srp_code: The SRP code to filter the requests by.
        :type srp_code: str
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The queryset for the model.
        :rtype: QuerySet
        """

        qs = self.model.objects.filter(
            srp_link__srp_code__iexact=srp_code
        ).prefetch_related(
            "srp_link",
            "srp_link__creator",
            "srp_link__creator__profile__main_character",
            "character",
            "ship",
            Prefetch(
                "srp_request_comments",
                queryset=RequestComment.objects.filter(
                    comment_type=RequestComment.Type.REQUEST_INFO
                ).order_by("pk"),
                to_attr="request_info_comments",
            ),
        )

        # Custom filters
        get_params = request.GET.dict()

        filter_request_status = get_params.get("filter[request_status]", None)

        if filter_request_status:
            logger.debug(
                f"Filtering SRP requests by request_status: {filter_request_status}"
            )

            qs = qs.filter(request_status=filter_request_status)

        return qs
