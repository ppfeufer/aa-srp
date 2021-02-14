# coding=utf-8

"""
Migrate comments from AaSrpRequest to AaSrpRequestComments
"""

from django.core.management import BaseCommand

from aasrp.models import (
    AaSrpRequest,
    AaSrpRequestStatus,
    AaSrpRequestComment,
    AaSrpRequestCommentType,
)


def get_input(text):
    """
    wrapped input to enable tz import
    """

    return input(text)


class Command(BaseCommand):
    """
    Migrate comments from AaSrpRequest to AaSrpRequestComments
    """

    help = "Migrate comments from AaSrpRequest to AaSrpRequestComments"

    def _migrate_reject_comments(self) -> None:
        """
        start migration
        :return:
        """

        srp_requests = AaSrpRequest.objects.all()

        self.stdout.write(
            self.style.WARNING(
                "Found {count} SRP requests.".format(count=srp_requests.count())
            )
        )

        if srp_requests.count() > 0:
            for srp_request in srp_requests:
                reject_reason = srp_request.reject_info
                srp_info = srp_request.additional_info

                # migrate additional info
                if srp_info != "":
                    self.stdout.write(
                        (
                            "Updating Request Information "
                            "for SRP request {request_code}".format(
                                request_code=srp_request.request_code
                            )
                        )
                    )

                    # check if there is already a request info
                    # for this request and remove it
                    AaSrpRequestComment.objects.filter(
                        srp_request=srp_request,
                        comment_type=AaSrpRequestCommentType.REQUEST_INFO,
                    ).delete()

                    # write new
                    srp_request_comment = AaSrpRequestComment()
                    srp_request_comment.srp_request = srp_request
                    srp_request_comment.comment = srp_info
                    srp_request_comment.comment_type = (
                        AaSrpRequestCommentType.REQUEST_INFO
                    )
                    srp_request_comment.creator = srp_request.creator
                    srp_request_comment.save()

                    # remove it from AaSrpRequest
                    srp_request.additional_info = ""
                    srp_request.save()

                # migrate reject reason
                if (
                    srp_request.request_status == AaSrpRequestStatus.REJECTED
                    and reject_reason != ""
                ):
                    self.stdout.write(
                        (
                            "Updating Reject Information "
                            "for SRP request {request_code}".format(
                                request_code=srp_request.request_code
                            )
                        )
                    )

                    # check if there is already a reject comment
                    # for this request and remove it
                    AaSrpRequestComment.objects.filter(
                        srp_request=srp_request,
                        comment_type=AaSrpRequestCommentType.REJECT_REASON,
                    ).delete()

                    # write new
                    srp_request_comment = AaSrpRequestComment()
                    srp_request_comment.srp_request = srp_request
                    srp_request_comment.comment = reject_reason
                    srp_request_comment.comment_type = (
                        AaSrpRequestCommentType.REJECT_REASON
                    )
                    srp_request_comment.save()

                    # remove it from AaSrpRequest
                    srp_request.reject_info = ""
                    srp_request.save()

    def handle(self, *args, **options):
        """
        ask before running ...
        :param args:
        :param options:
        """

        self.stdout.write(
            "This command will migrate the reject comments "
            "from AaSrpRequest to AaSrpRequestComments"
        )

        user_input = get_input("Are you sure you want to proceed? (yes/no)?")

        if user_input == "yes":
            self.stdout.write("Starting migration. Please stand by.")
            self._migrate_reject_comments()
            self.stdout.write(self.style.SUCCESS("Update complete!"))
        else:
            self.stdout.write(self.style.WARNING("Aborted."))
