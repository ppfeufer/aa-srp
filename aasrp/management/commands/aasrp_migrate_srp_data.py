"""
Migrate srp data from the built-in SRP module.

This script defines a Django management command to migrate SRP (Ship Replacement Program) data
from the built-in SRP module to the AA SRP module. It handles the migration of SRP fleets and
their associated requests, ensuring data integrity and avoiding duplication.
"""

# Django
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

# Alliance Auth
from allianceauth.srp.models import SrpFleetMain

# AA SRP
from aasrp.helper.character import get_user_for_character
from aasrp.models import RequestComment, Setting, SrpLink, SrpRequest
from aasrp.providers import esi


def get_input(text):
    """
    Wrapped input function to prompt the user during the migration process.

    :param text: The text to display as the input prompt.
    :type text: str
    :return: The user's input.
    :rtype: str
    """

    return input(text)


class Command(BaseCommand):
    """
    Django management command to migrate SRP data from the built-in SRP module.

    This command migrates SRP fleets and their associated requests, ensuring that
    all data is properly transferred to the AA SRP module. It also marks migrated
    SRP links as completed to prevent duplication.
    """

    help = "Migrate SRP data from the built-in SRP module"

    # Cache for ship info to minimize ESI calls
    ship_info_cache = {}

    def _get_ship_info_from_esi_by_id(self, ship_type_id):
        """
        Retrieve ship information from ESI by ship type ID, with caching to avoid redundant API calls.

        :param ship_type_id:
        :type ship_type_id:
        :return:
        :rtype:
        """

        if ship_type_id not in self.ship_info_cache:
            self.stdout.write(f"Adding ship info for type ID {ship_type_id} to cache")

            self.ship_info_cache[ship_type_id] = (
                esi.client.Universe.GetUniverseTypesTypeId(
                    type_id=ship_type_id
                ).result()
            )

        return self.ship_info_cache[ship_type_id]

    def _migrate_srp_data(self):  # pylint: disable=too-many-locals, too-many-statements
        """
        Perform the migration of SRP data.

        This method migrates SRP fleets and their associated requests from the built-in
        SRP module to the AA SRP module. It ensures that all necessary fields are properly
        mapped and handles cases where data might be missing or invalid.

        :return: None
        :rtype: None
        """

        srp_links_migrated = 0
        srp_links_skipped = 0
        srp_requests_migrated = 0
        srp_requests_skipped = 0

        self.stdout.write("Migrating SRP fleets ...")
        srp_fleets = SrpFleetMain.objects.all()

        # Retrieve the loss value field setting
        loss_value_field = Setting.objects.get_setting(Setting.Field.LOSS_VALUE_SOURCE)

        for srp_fleet in srp_fleets:
            # Check if the fleet creator is valid
            srp_fleet_creator = get_user_for_character(
                character=srp_fleet.fleet_commander
            )

            if srp_fleet_creator is not None:
                # Extract fleet details
                srp_fleet_commander = srp_fleet.fleet_commander
                srp_fleet_name = srp_fleet.fleet_name
                srp_fleet_doctrine = srp_fleet.fleet_doctrine
                srp_fleet_time = srp_fleet.fleet_time
                srp_fleet_aar_link = srp_fleet.fleet_srp_aar_link

                # Determine the SRP fleet status
                srp_fleet_status = SrpLink.Status.ACTIVE
                if srp_fleet.fleet_srp_status == "Completed":
                    srp_fleet_status = SrpLink.Status.COMPLETED

                if srp_fleet.fleet_srp_code == "":
                    srp_fleet_status = SrpLink.Status.CLOSED
                    srp_fleet.fleet_srp_code = get_random_string(length=8)

                srp_fleet_srp_code = srp_fleet.fleet_srp_code

                self.stdout.write(f"Migrating SRP fleet {srp_fleet_srp_code} …")

                try:
                    # Check if the SRP link already exists
                    srp_link = SrpLink.objects.get(srp_code=srp_fleet_srp_code)

                    srp_links_skipped += 1
                except SrpLink.DoesNotExist:
                    # Create a new SRP link
                    srp_link = SrpLink()
                    srp_link.srp_name = srp_fleet_name
                    srp_link.srp_status = srp_fleet_status
                    srp_link.srp_code = srp_fleet_srp_code
                    srp_link.fleet_doctrine = srp_fleet_doctrine
                    srp_link.aar_link = srp_fleet_aar_link
                    srp_link.fleet_time = srp_fleet_time
                    srp_link.fleet_commander = srp_fleet_commander
                    srp_link.creator = srp_fleet_creator
                    srp_link.save()

                    srp_fleet.fleet_srp_status = "Completed"
                    srp_fleet.save()

                    srp_links_migrated += 1

                self.stdout.write(
                    f"Migrating SRP requests for SRP fleet {srp_fleet_srp_code} ..."
                )

                srp_userrequests = srp_fleet.srpuserrequest_set.all()

                for srp_userrequest in srp_userrequests:
                    # Check if the request creator is valid
                    srp_userrequest_creator = get_user_for_character(
                        character=srp_userrequest.character
                    )

                    if (
                        srp_userrequest_creator is not None
                        and srp_userrequest.character is not None
                    ):
                        srp_userrequest_killboard_link = srp_userrequest.killboard_link

                        try:
                            # Check if the SRP request already exists
                            SrpRequest.objects.get(
                                killboard_link=srp_userrequest_killboard_link
                            )

                            srp_requests_skipped += 1
                        except SrpRequest.DoesNotExist:
                            # Create a new SRP request
                            srp_userrequest_additional_info = (
                                srp_userrequest.additional_info
                            )
                            srp_userrequest_payout = srp_userrequest.srp_total_amount
                            srp_userrequest_loss_amount = srp_userrequest.kb_total_loss

                            srp_kill_link = SrpRequest.objects.get_kill_id(
                                srp_userrequest_killboard_link
                            )

                            (
                                ship_type_id,
                                ship_value,  # pylint: disable=unused-variable
                                victim_id,  # pylint: disable=unused-variable
                            ) = SrpRequest.objects.get_kill_data(
                                killmail_id=srp_kill_link,
                                loss_value_field=loss_value_field,
                            )

                            srp_userrequest_ship = self._get_ship_info_from_esi_by_id(
                                ship_type_id
                            )

                            srp_userrequest_post_time = srp_userrequest.post_time
                            srp_userrequest_request_code = get_random_string(length=16)
                            srp_userrequest_character = srp_userrequest.character
                            srp_userrequest_srp_link = srp_link

                            srp_userrequest_status = SrpRequest.Status.PENDING
                            if srp_userrequest.srp_status == "Approved":
                                srp_userrequest_status = SrpRequest.Status.APPROVED

                            if srp_userrequest.srp_status == "Rejected":
                                srp_userrequest_status = SrpRequest.Status.REJECTED

                            srp_request = SrpRequest()
                            srp_request.killboard_link = srp_userrequest_killboard_link
                            srp_request.request_status = srp_userrequest_status
                            srp_request.payout_amount = srp_userrequest_payout
                            srp_request.loss_amount = srp_userrequest_loss_amount
                            srp_request.ship_name = srp_userrequest_ship.name
                            srp_request.ship_id = ship_type_id
                            srp_request.post_time = srp_userrequest_post_time
                            srp_request.request_code = srp_userrequest_request_code
                            srp_request.character = srp_userrequest_character
                            srp_request.creator = srp_userrequest_creator
                            srp_request.srp_link = srp_userrequest_srp_link
                            srp_request.save()

                            # Add request info as a comment
                            srp_request_comment = RequestComment()
                            srp_request_comment.comment = (
                                srp_userrequest_additional_info
                            )
                            srp_request_comment.srp_request = srp_request
                            srp_request_comment.comment_type = (
                                RequestComment.Type.REQUEST_INFO
                            )
                            srp_request_comment.creator = srp_userrequest_creator
                            srp_request_comment.save()

                            srp_requests_migrated += 1

        self.stdout.write("Migration finished.")
        self.stdout.write(f"SRP links migrated: {srp_links_migrated}")
        self.stdout.write(f"SRP links skipped: {srp_links_skipped}")
        self.stdout.write(f"SRP requests migrated: {srp_requests_migrated}")
        self.stdout.write(f"SRP requests skipped: {srp_requests_skipped}")

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        """
        Prompt the user and execute the migration process.

        This method asks the user for confirmation before starting the migration process.
        If the user confirms, it calls the `_migrate_srp_data` method to perform the migration.

        :param args: Positional arguments passed to the command.
        :type args: tuple
        :param options: Keyword arguments passed to the command.
        :type options: dict
        :return: None
        :rtype: None
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

        self.stdout.write(
            self.style.ERROR("!!! Make sure you have NO pending SRP requests !!!")
        )

        user_input = get_input("Are you sure you want to proceed? (yes/no)?")

        if user_input == "yes":
            self.stdout.write("Starting migration. Please stand by.")
            self._migrate_srp_data()
            self.stdout.write(self.style.SUCCESS("Migration complete!"))
        else:
            self.stdout.write(self.style.WARNING("Aborted."))
