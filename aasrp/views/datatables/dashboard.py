"""
Dashboard SRP links DataTables view for Alliance Auth SRP module.
"""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q, QuerySet
from django.http.request import HttpRequest

# Alliance Auth
from allianceauth.framework.datatables import DataTablesView
from allianceauth.services.hooks import get_extension_logger

# AA SRP
from aasrp.models import SrpLink, SrpRequest
from aasrp.providers.applogger import AppLogger

logger = AppLogger(my_logger=get_extension_logger(name=__name__))


class DashboardSrpLinksView(PermissionRequiredMixin, DataTablesView):
    """
    Datatables view for SRP links on the dashboard.
    """

    permission_required = "aasrp.basic_access"
    show_all_links = False
    model = SrpLink

    columns = [
        ("srp_name", "aasrp/partials/datatables/dashboard/column-srp-name.html"),
        (
            "creator__profile__main_character__character_name",
            "aasrp/partials/datatables/dashboard/column-creator-name.html",
        ),
        ("fleet_time", "aasrp/partials/datatables/dashboard/column-fleet-time.html"),
        (
            "fleet_type__name",
            "aasrp/partials/datatables/dashboard/column-fleet-type.html",
        ),
        (
            "fleet_doctrine",
            "aasrp/partials/datatables/dashboard/column-fleet-doctrine.html",
        ),
        ("aar_link", "aasrp/partials/datatables/dashboard/column-aar-link.html"),
        ("srp_code", "aasrp/partials/datatables/dashboard/column-srp-code.html"),
        ("", "aasrp/partials/datatables/dashboard/column-total-cost.html"),
        ("srp_status", "aasrp/partials/datatables/dashboard/column-srp-status.html"),
        ("", "aasrp/partials/datatables/dashboard/column-request-count.html"),
        ("", "aasrp/partials/datatables/dashboard/column-actions.html"),
    ]

    logger.debug("DashboardSrpLinksView initialized with columns: %s", columns)

    def get_model_qs(
        self, request: HttpRequest, *args, **kwargs  # pylint: disable=unused-argument
    ) -> QuerySet[SrpLink]:
        """
        Get the queryset for the model.

        :param request:
        :type request:
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        srp_links = self.model.objects.prefetch_related(
            "fleet_commander",
            "creator",
            "creator__profile__main_character",
            "srp_requests",
        ).all()

        if not self.show_all_links:
            srp_links = srp_links.filter(srp_status=SrpLink.Status.ACTIVE)

        # Custom filters
        get_params = request.GET.dict()

        # Filter for SRP links that have pending requests
        filter_has_requests = (
            get_params.get("filter[has_requests]", "false").lower() == "true"
        )

        if filter_has_requests:
            srp_links = srp_links.annotate(
                pending_count=Count(
                    "srp_requests",
                    filter=Q(srp_requests__request_status=SrpRequest.Status.PENDING),
                )
            ).filter(pending_count__gt=0)

        return srp_links
