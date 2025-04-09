"""
Migrate srp data from the built-in SRP module
"""

# Django
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

# Alliance Auth
from allianceauth.srp.models import SrpFleetMain

# Alliance Auth (External Libs)
from eveuniverse.models import EveType

# AA SRP
from aasrp.helper.character import get_user_for_character
from aasrp.models import RequestComment, SrpLink, SrpRequest


def get_input(text):
    """
    Wrapped input to migrate srp data
    """

    return input(text)


class Command(BaseCommand):
    """
    Migrate SRP data from the built-in SRP module
    """

    help = "Migrate SRP data from the built-in SRP module"

    def _migrate_srp_data(  # pylint: disable=too-many-locals, too-many-statements
        self,
    ) -> None:
        """
        Migrate srp data from the built-in SRP module

        :return:
        :rtype:
        """

        srp_links_migrated = 0
        srp_links_skipped = 0
        srp_requests_migrated = 0
        srp_requests_skipped = 0

        self.stdout.write("Migrating SRP fleets ...")
        srp_fleets = SrpFleetMain.objects.all()

        for srp_fleet in srp_fleets:
            # Let's see if the creator is still valid
            # Returns None when the creators account has been deleted
            # and no sentinel user can be created or obtained
            # in this case, we cannot create the fleet again
            srp_fleet_creator = get_user_for_character(
                character=srp_fleet.fleet_commander
            )

            if srp_fleet_creator is not None:
                srp_fleet_commander = srp_fleet.fleet_commander
                srp_fleet_name = srp_fleet.fleet_name
                srp_fleet_doctrine = srp_fleet.fleet_doctrine
                srp_fleet_time = srp_fleet.fleet_time
                srp_fleet_aar_link = srp_fleet.fleet_srp_aar_link

                # Fix srp status
                srp_fleet_status = SrpLink.Status.ACTIVE
                if srp_fleet.fleet_srp_status == "Completed":
                    srp_fleet_status = SrpLink.Status.COMPLETED

                if srp_fleet.fleet_srp_code == "":
                    srp_fleet_status = SrpLink.Status.CLOSED

                    # Also fix the missing SRP code, we need it!
                    srp_fleet.fleet_srp_code = get_random_string(
                        length=8  # 8 chars only because it's an old SRP link
                    )

                srp_fleet_srp_code = srp_fleet.fleet_srp_code

                self.stdout.write(f"Migrating SRP fleet {srp_fleet_srp_code} …")

                try:
                    srp_link = SrpLink.objects.get(srp_code=srp_fleet_srp_code)

                    srp_links_skipped += 1
                except SrpLink.DoesNotExist:
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

                    # Mark migrated the SRP link as COMPLETED and save the object
                    srp_fleet.fleet_srp_status = "Completed"
                    srp_fleet.save()

                    srp_links_migrated += 1

                    # get the new srp link object
                    srp_link = SrpLink.objects.get(srp_code=srp_fleet_srp_code)

                self.stdout.write(
                    f"Migrating SRP requests for SRP fleet {srp_fleet_srp_code} ..."
                )
                srp_userrequests = srp_fleet.srpuserrequest_set.all()

                for srp_userrequest in srp_userrequests:
                    # Let's see if the creator is still valid
                    # Returns None when the creators' account has been deleted
                    # and no sentinel user can be created or obtained
                    # in this case, we cannot create the request again
                    srp_userrequest_creator = get_user_for_character(
                        character=srp_userrequest.character
                    )

                    if (
                        srp_userrequest_creator is not None
                        and srp_userrequest.character is not None
                    ):
                        srp_userrequest_killboard_link = srp_userrequest.killboard_link

                        try:
                            SrpRequest.objects.get(
                                killboard_link=srp_userrequest_killboard_link
                            )

                            srp_requests_skipped += 1
                        except SrpRequest.DoesNotExist:
                            srp_userrequest_additional_info = (
                                srp_userrequest.additional_info
                            )
                            srp_userrequest_payout = srp_userrequest.srp_total_amount
                            srp_userrequest_loss_amount = srp_userrequest.kb_total_loss

                            try:
                                srp_userrequest_ship = EveType.objects.get(
                                    name=srp_userrequest.srp_ship_name
                                )
                            except EveType.DoesNotExist:
                                srp_kill_link = SrpRequest.objects.get_kill_id(
                                    srp_userrequest_killboard_link
                                )

                                (
                                    ship_type_id,
                                    ship_value,  # pylint: disable=unused-variable
                                    victim_id,  # pylint: disable=unused-variable
                                ) = SrpRequest.objects.get_kill_data(srp_kill_link)

                                (
                                    srp_userrequest_ship,
                                    created_from_esi,  # pylint: disable=unused-variable
                                ) = EveType.objects.get_or_create_esi(id=ship_type_id)

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
                            srp_request.ship = srp_userrequest_ship
                            srp_request.post_time = srp_userrequest_post_time
                            srp_request.request_code = srp_userrequest_request_code
                            srp_request.character = srp_userrequest_character
                            srp_request.creator = srp_userrequest_creator
                            srp_request.srp_link = srp_userrequest_srp_link
                            srp_request.save()

                            # add request info to comments
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
        Ask before running ...

        :param args:
        :type args:
        :param options:
        :type options:
        :return:
        :rtype:
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
