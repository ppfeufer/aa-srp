# coding=utf-8

"""
Our Models
"""

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from eveuniverse.models import EveType

from allianceauth.eveonline.models import EveCharacter


def get_sentinel_user():
    """
    get user or create one
    :return:
    """

    return User.objects.get_or_create(username="deleted")[0]


class AaSrpStatus(models.TextChoices):
    """
    Choices for SRP Status
    """

    ACTIVE = "Active", _("Active")
    CLOSED = "Closed", _("Closed")
    COMPLETED = "Completed", _("Completed")


class AaSrpRequestStatus(models.TextChoices):
    """
    Choices for SRP Request Status
    """

    PENDING = "Pending", _("Pending")
    APPROVED = "Approved", _("Approved")
    REJECTED = "Rejected", _("Rejected")


class AaSrpRequestCommentType(models.TextChoices):
    """
    Choices for Comment Types
    """

    COMMENT = "Comment", _("SRP Request Comment")
    REQUEST_INFO = "Request Information", _("SRP Request Additional Information")
    REJECT_REASON = "Reject Reason", _("SRP Reject Reason")


class AaSrp(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:
        verbose_name = "AA-SRP"
        managed = False
        default_permissions = ()
        permissions = (
            # can open the SRP app and submit SRP requests
            ("basic_access", "Can access the AA-SRP module"),
            # can create SRP links
            ("create_srp", "Can create new SRP links"),
            # can manage the complete SRP module
            ("manage_srp", "Can manage SRP"),
            # can manage SRP requests only
            ("manage_srp_requests", "Can manage SRP requests"),
        )


class AaSrpLink(models.Model):
    """
    SRP Link model
    """

    srp_name = models.CharField(max_length=254, default="")
    srp_status = models.CharField(
        max_length=9,
        choices=AaSrpStatus.choices,
        default=AaSrpStatus.ACTIVE,
    )
    srp_code = models.CharField(max_length=16, default="")
    fleet_commander = models.ForeignKey(
        EveCharacter,
        related_name="+",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
    )
    fleet_doctrine = models.CharField(max_length=254, default="")
    fleet_time = models.DateTimeField()
    aar_link = models.CharField(max_length=254, blank=True, default="")

    creator = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET(get_sentinel_user),
        help_text=_("Who created the SRP link?"),
    )

    def __str__(self):
        return self.srp_name

    @property
    def total_cost(self):
        """
        total cost for this SRP link
        :return:
        """

        return sum([int(r.payout_amount) for r in self.aasrprequest_set.all()])

    @property
    def total_requests(self):
        """
        Number of total SRP requests
        :return:
        """

        return self.aasrprequest_set.count()

    @property
    def pending_requests(self):
        """
        Number of pending SRP requests
        :return:
        """

        return self.aasrprequest_set.filter(
            request_status=AaSrpRequestStatus.PENDING
        ).count()

    @property
    def approved_requests(self):
        """
        Number of approved SRP requests
        :return:
        """

        return self.aasrprequest_set.filter(
            request_status=AaSrpRequestStatus.APPROVED
        ).count()

    @property
    def rejected_requests(self):
        """
        Number of rejected SRP requests
        :return:
        """

        return self.aasrprequest_set.filter(
            request_status=AaSrpRequestStatus.REJECTED
        ).count()

    @property
    def requests(self):
        """
        All SRP requests
        :return:
        """

        return self.aasrprequest_set.all()

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("SRP Link")
        verbose_name_plural = _("SRP Links")


class AaSrpRequest(models.Model):
    """
    SRP Request model
    """

    request_code = models.CharField(max_length=254, default="")
    creator = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET(get_sentinel_user),
        help_text=_("Who created the SRP link?"),
    )
    character = models.ForeignKey(EveCharacter, null=True, on_delete=models.SET_NULL)
    ship_name = models.CharField(max_length=254, default="")
    ship = models.ForeignKey(
        EveType,
        related_name="+",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
    )
    killboard_link = models.CharField(max_length=254, default="")
    additional_info = models.TextField(blank=True, default="")
    request_status = models.CharField(
        max_length=8,
        choices=AaSrpRequestStatus.choices,
        default=AaSrpRequestStatus.PENDING,
    )
    payout_amount = models.BigIntegerField(default=0)
    srp_link = models.ForeignKey(AaSrpLink, on_delete=models.CASCADE)
    loss_amount = models.BigIntegerField(default=0)
    post_time = models.DateTimeField(default=timezone.now)
    reject_info = models.TextField(blank=True, default="")

    def __str__(self):
        return _(
            "{character_name} ({user_name}) SRP Request "
            "for: {ship} ({request_code})".format(
                character_name=self.character.character_name,
                user_name=self.creator.profile.main_character.character_name,
                ship=self.ship.name,
                request_code=self.request_code,
            )
        )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("SRP Request")
        verbose_name_plural = _("SRP Requests")


class AaSrpRequestComment(models.Model):
    """
    SRP Request Comments model
    """

    comment = models.TextField(null=True, blank=True)

    comment_type = models.CharField(
        max_length=19,
        choices=AaSrpRequestCommentType.choices,
        default=AaSrpRequestCommentType.COMMENT,
    )

    creator = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET(get_sentinel_user),
    )

    srp_request = models.ForeignKey(
        AaSrpRequest,
        related_name="+",
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("SRP Request Comment")
        verbose_name_plural = _("SRP Request Comments")
