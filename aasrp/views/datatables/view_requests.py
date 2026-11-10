"""
Datatables view for SRP requests.
"""

# Standard Library
import json

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q, QuerySet, Sum
from django.db.models.query import Prefetch
from django.http import JsonResponse
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
            "ship__name",
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

    def handle_request(
        self, request: HttpRequest, params: dict, *args, **kwargs
    ) -> JsonResponse:
        """
        Add fleet-wide request statistics to the server-side DataTables response.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :param params: The parameters for the DataTables request.
        :type params: dict
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A JsonResponse containing the DataTables response with the summary.
        :rtype: JsonResponse
        """

        response = super().handle_request(request, params, *args, **kwargs)
        response_data = json.loads(response.content)
        response_data["summary"] = self._get_summary(srp_code=str(kwargs["srp_code"]))

        return JsonResponse(response_data)

    @staticmethod
    def _get_summary(srp_code: str) -> dict:
        """
        Get a summary of SRP requests for a given SRP code.
        Calculate counts and payout totals for every request on an SRP link.

        :param srp_code: The SRP code to filter the requests by.
        :type srp_code: str
        :return: A dictionary containing the summary of SRP requests.
        :rtype: dict
        """

        summary = SrpRequest.objects.filter(
            srp_link__srp_code__iexact=srp_code
        ).aggregate(
            requestsTotal=Count("pk"),
            requestsPending=Count(
                "pk", filter=Q(request_status=SrpRequest.Status.PENDING)
            ),
            requestsApproved=Count(
                "pk", filter=Q(request_status=SrpRequest.Status.APPROVED)
            ),
            requestsRejected=Count(
                "pk", filter=Q(request_status=SrpRequest.Status.REJECTED)
            ),
            totalSrpAmount=Sum(
                "payout_amount",
                filter=Q(request_status=SrpRequest.Status.APPROVED),
            ),
            pendingSrpAmount=Sum(
                "payout_amount",
                filter=Q(request_status=SrpRequest.Status.PENDING),
            ),
        )

        return {key: value or 0 for key, value in summary.items()}

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

        qs = (
            self.model.objects.filter(srp_link__srp_code__iexact=srp_code)
            .prefetch_related(
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
            .distinct()
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
