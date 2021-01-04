# coding=utf-8

"""
Migrate srp data from the built-in SRP module
"""

from django.core.management.base import BaseCommand

from aasrp.models import AaSrpRequest
from eveuniverse.models import EveType


def get_input(text):
    """
    wrapped input to enable tz import
    """

    return input(text)


class Command(BaseCommand):
    help = "Update DB Relations"

    def _update_relations(self) -> None:
        """
        updating relations in database
        :return:
        """

        srp_requests = AaSrpRequest.objects.filter(ship=None)

        self.stdout.write(
            self.style.WARNING(
                "{count} SRP requests need to be updated".format(
                    count=srp_requests.count()
                )
            )
        )

        for srp_request in srp_requests:
            self.stdout.write(
                "Updating SRP request {request_code}".format(
                    request_code=srp_request.request_code
                )
            )

            eve_type = EveType.objects.get(name=srp_request.ship_name)

            srp_request.ship = eve_type
            srp_request.save()

    def handle(self, *args, **options):
        """
        ask before running ...
        :param args:
        :param options:
        """

        self.stdout.write(
            "This will update the relations between various tables in the database."
        )

        user_input = get_input("Are you sure you want to proceed? (yes/no)?")

        if user_input == "yes":
            self.stdout.write("Starting migration. Please stand by.")
            self._update_relations()
            self.stdout.write(self.style.SUCCESS("Update complete!"))
        else:
            self.stdout.write(self.style.WARNING("Aborted."))
