"""
Our Models
"""

# Django
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from eveuniverse.models import EveType


def get_sentinel_user():
    """
    get user or create one
    :return:
    """

    return User.objects.get_or_create(username="deleted")[0]


class AaSrp(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:
        """
        General definitions
        """

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

    class Status(models.TextChoices):
        """
        Choices for SRP Status
        """

        ACTIVE = "Active", _("Active")
        CLOSED = "Closed", _("Closed")
        COMPLETED = "Completed", _("Completed")

    srp_name = models.CharField(max_length=254, default="")
    srp_status = models.CharField(
        max_length=9, choices=Status.choices, default=Status.ACTIVE
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

    def __str__(self) -> str:
        return str(self.srp_name)

    @property
    def total_cost(self):
        """
        total cost for this SRP link
        :return:
        """

        return sum(
            int(r.payout_amount)
            for r in self.srp_requests.filter(request_status="Approved")
        )

    @property
    def total_requests(self):
        """
        Number of total SRP requests
        :return:
        """

        return self.srp_requests.count()

    @property
    def pending_requests(self):
        """
        Number of pending SRP requests
        :return:
        """

        return self.srp_requests.filter(
            request_status=AaSrpRequest.Status.PENDING
        ).count()

    @property
    def approved_requests(self):
        """
        Number of approved SRP requests
        :return:
        """

        return self.srp_requests.filter(
            request_status=AaSrpRequest.Status.APPROVED
        ).count()

    @property
    def rejected_requests(self):
        """
        Number of rejected SRP requests
        :return:
        """

        return self.srp_requests.filter(
            request_status=AaSrpRequest.Status.REJECTED
        ).count()

    @property
    def requests(self):
        """
        All SRP requests
        :return:
        """

        return self.srp_requests.all()

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

    class Status(models.TextChoices):
        """
        Choices for SRP Request Status
        """

        PENDING = "Pending", _("Pending")
        APPROVED = "Approved", _("Approved")
        REJECTED = "Rejected", _("Rejected")

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
        related_name="srp_requests",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
    )
    killboard_link = models.CharField(max_length=254, default="")
    additional_info = models.TextField(blank=True, default="")
    request_status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.PENDING
    )
    payout_amount = models.BigIntegerField(default=0)
    srp_link = models.ForeignKey(
        AaSrpLink, related_name="srp_requests", on_delete=models.CASCADE
    )
    loss_amount = models.BigIntegerField(default=0)
    post_time = models.DateTimeField(default=timezone.now)
    reject_info = models.TextField(blank=True, default="")

    def __str__(self):
        character_name = self.character.character_name
        user_name = self.creator.profile.main_character.character_name
        ship = self.ship.name
        request_code = self.request_code

        return _(
            f"{character_name} ({user_name}) SRP Request for: {ship} ({request_code})"
        )

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("SRP Request")
        verbose_name_plural = _("SRP Requests")


class AaSrpInsurance(models.Model):
    """
    Insurance Model
    """

    srp_request = models.ForeignKey(
        AaSrpRequest, on_delete=models.CASCADE, related_name="insurance"
    )
    insurance_level = models.CharField(max_length=254, default="")
    insurance_cost = models.FloatField()
    insurance_payout = models.FloatField()

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("Ship Insurance")
        verbose_name_plural = _("Ship Insurances")


class AaSrpRequestComment(models.Model):
    """
    SRP Request Comments model
    """

    class Type(models.TextChoices):
        """
        Choices for Comment Types
        """

        COMMENT = "Comment", _("SRP Request Comment")
        REQUEST_INFO = "Request Information", _("SRP Request Additional Information")
        REJECT_REASON = "Reject Reason", _("SRP Reject Reason")

    comment = models.TextField(null=True, blank=True)

    comment_type = models.CharField(
        max_length=19, choices=Type.choices, default=Type.COMMENT
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
        related_name="srp_request_comments",
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


class AaSrpUserSettings(models.Model):
    """
    User settings
    """

    user = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET(get_sentinel_user),
    )

    disable_notifications = models.BooleanField(default=False)

    class Meta:
        """
        Meta definitions
        """

        default_permissions = ()
        verbose_name = _("User Settings")
        verbose_name_plural = _("User Settings")
