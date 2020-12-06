# coding=utf-8

"""
Migrate srp data from the built-in SRP module
"""

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from aasrp.view_helper import get_user_for_character
from aasrp.models import AaSrpLink, AaSrpRequest, AaSrpStatus, AaSrpRequestStatus

from allianceauth.srp.models import SrpFleetMain


def get_input(text):
    """
    wrapped input to enable tz import
    """

    return input(text)


class Command(BaseCommand):
    help = "Migrate srp data from the built-in SRP module"

    def _migrate_srp_data(self) -> None:
        """
        migrate srp data from the built-in SRP module
        :return:
        """

        srp_links_migrated = 0
        srp_links_skipped = 0
        srp_requests_migrated = 0
        srp_requests_skipped = 0

        self.stdout.write("Migrating SRP fleets ...")
        srp_fleets = SrpFleetMain.objects.all()
        for srp_fleet in srp_fleets:

            srp_fleet_name = srp_fleet.fleet_name
            srp_fleet_doctrine = srp_fleet.fleet_doctrine
            srp_fleet_time = srp_fleet.fleet_time
            srp_fleet_commander = srp_fleet.fleet_commander
            srp_fleet_creator = get_user_for_character(character=srp_fleet_commander)
            srp_fleet_aar_link = srp_fleet.fleet_srp_aar_link

            # fix srp status
            srp_fleet_status = AaSrpStatus.ACTIVE
            if srp_fleet.fleet_srp_status == "Completed":
                srp_fleet_status = AaSrpStatus.COMPLETED

            if srp_fleet.fleet_srp_code == "":
                srp_fleet_status = AaSrpStatus.CLOSED

                # also fix the missing SRP code, we need it!
                srp_fleet.fleet_srp_code = get_random_string(
                    length=8
                )  # 8 chars only because old SRP link

            srp_fleet_srp_code = srp_fleet.fleet_srp_code

            self.stdout.write(
                "Migrating SRP fleet {srp_code} ...".format(srp_code=srp_fleet_srp_code)
            )

            try:
                srp_link = AaSrpLink.objects.get(srp_code=srp_fleet_srp_code)

                srp_links_skipped += 1
            except AaSrpLink.DoesNotExist:
                srp_link = AaSrpLink()

                srp_link.srp_name = srp_fleet_name
                srp_link.srp_status = srp_fleet_status
                srp_link.srp_code = srp_fleet_srp_code
                srp_link.fleet_doctrine = srp_fleet_doctrine
                srp_link.aar_link = srp_fleet_aar_link
                srp_link.fleet_time = srp_fleet_time
                srp_link.fleet_commander = srp_fleet_commander
                srp_link.creator = srp_fleet_creator
                srp_link.save()

                # mark migrated SRP link as COMPLETED and save the object
                srp_fleet.fleet_srp_status = "Completed"
                srp_fleet.save()

                srp_links_migrated += 1

                # get the new srp link object
                srp_link = AaSrpLink.objects.get(srp_code=srp_fleet_srp_code)

            self.stdout.write(
                "Migrating SRP requests for SRP fleet {srp_code} ...".format(
                    srp_code=srp_fleet_srp_code
                )
            )
            srp_userrequests = srp_fleet.srpuserrequest_set.all()
            for srp_userrequest in srp_userrequests:
                srp_userrequest_killboard_link = srp_userrequest.killboard_link
                srp_userrequest_additional_info = srp_userrequest.additional_info
                srp_userrequest_payout = srp_userrequest.srp_total_amount
                srp_userrequest_loss_amount = srp_userrequest.kb_total_loss
                srp_userrequest_ship_name = srp_userrequest.srp_ship_name
                srp_userrequest_post_time = srp_userrequest.post_time
                srp_userrequest_request_code = get_random_string(length=16)
                srp_userrequest_character = srp_userrequest.character
                srp_userrequest_creator = get_user_for_character(
                    character=srp_userrequest_character
                )
                srp_userrequest_srp_link = srp_link

                srp_userrequest_status = AaSrpRequestStatus.PENDING
                if srp_userrequest.srp_status == "Approved":
                    srp_userrequest_status = AaSrpRequestStatus.APPROVED

                if srp_userrequest.srp_status == "Rejected":
                    srp_userrequest_status = AaSrpRequestStatus.REJECTED

                try:
                    AaSrpRequest.objects.get(
                        killboard_link=srp_userrequest_killboard_link
                    )

                    srp_requests_skipped += 1
                except AaSrpRequest.DoesNotExist:
                    srp_request = AaSrpRequest()

                    srp_request.killboard_link = srp_userrequest_killboard_link
                    srp_request.additional_info = srp_userrequest_additional_info
                    srp_request.request_status = srp_userrequest_status
                    srp_request.payout_amount = srp_userrequest_payout
                    srp_request.loss_amount = srp_userrequest_loss_amount
                    srp_request.ship_name = srp_userrequest_ship_name
                    srp_request.post_time = srp_userrequest_post_time
                    srp_request.request_code = srp_userrequest_request_code
                    srp_request.character = srp_userrequest_character
                    srp_request.creator = srp_userrequest_creator
                    srp_request.srp_link = srp_userrequest_srp_link
                    srp_request.save()

                    srp_requests_migrated += 1

        self.stdout.write("Migration finished.")

        self.stdout.write(
            "SRP links migrated: {srp_links_migrated}".format(
                srp_links_migrated=srp_links_migrated
            )
        )
        self.stdout.write(
            "SRP links skipped: {srp_links_skipped}".format(
                srp_links_skipped=srp_links_skipped
            )
        )

        self.stdout.write(
            "SRP requests migrated: {srp_requests_migrated}".format(
                srp_requests_migrated=srp_requests_migrated
            )
        )
        self.stdout.write(
            "SRP requests skipped: {srp_requests_skipped}".format(
                srp_requests_skipped=srp_requests_skipped
            )
        )

    def handle(self, *args, **options):
        """
        ask before running ...
        :param args:
        :param options:
        """

        self.stdout.write(
            "Migrating SRP links and requests from the built-in SRP module."
        )
        self.stdout.write(
            self.style.WARNING(
                "Due to the nature of the built-in modules design, "
                "ALL SRP links in the built-in module will be marked as COMPLETED "
                "after their migration so they cannot be migrated again and we "
                "don't end up with duplicates!"
            )
        )

        user_input = get_input("Are you sure you want to proceed? (yes/no)?")

        if user_input == "yes":
            self.stdout.write("Starting migration. Please stand by.")
            self._migrate_srp_data()
            self.stdout.write(self.style.SUCCESS("Migration complete!"))
        else:
            self.stdout.write(self.style.WARNING("Aborted."))