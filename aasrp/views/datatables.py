"""
Datatables views for AA-SRP app.
"""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest

# Alliance Auth
from allianceauth.framework.datatables import DataTablesView
from allianceauth.services.hooks import get_extension_logger

# AA SRP
from aasrp import __title__
from aasrp.models import SrpRequest
from aasrp.providers import AppLogger

logger = AppLogger(my_logger=get_extension_logger(name=__name__), prefix=__title__)


class OwnSrpRequestsView(PermissionRequiredMixin, DataTablesView):
    """
    Datatables view for own SRP requests.
    """

    permission_required = "aasrp.basic_access"
    model = SrpRequest
    visible_columns = [
        ("post_time", "{{ row.post_time.isoformat }}"),
        (
            "character__character_name",
            "aasrp/partials/datatables/view-own-requests/column-character.html",
        ),
        (
            "srp_link__srp_name",
            "aasrp/partials/datatables/view-own-requests/column-request-details.html",
        ),
        ("ship__name", "aasrp/partials/datatables/view-own-requests/column-ship.html"),
        ("loss_amount", "{{ row.loss_amount }}"),
        ("payout_amount", "{{ row.payout_amount }}"),
        ("", "aasrp/partials/datatables/view-own-requests/column-status.html"),
    ]
    invisible_columns = [
        ("srp_link__srp_code", "{{ row.srp_link.srp_code }}"),
        ("request_code", "{{ row.request_code }}"),
        ("request_status", "{{ row.request_status }}"),
        ("killboard_link", "{{ row.killboard_link }}"),
    ]
    columns = visible_columns + invisible_columns

    logger.debug("OwnSrpRequestsView initialized with columns: %s", columns)

    def get_model_qs(
        self, request: HttpRequest, *args, **kwargs  # pylint: disable=unused-argument
    ) -> QuerySet:
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

        qs = (
            self.model.objects.filter(creator=request.user)
            # .filter(ship__isnull=False)  # Uncomment to filter out requests without a ship
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

        return qs
