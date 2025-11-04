"""
Form definitions for the AA-SRP application.
"""

# Standard Library
import re

# Django
from django import forms
from django.forms import ModelForm
from django.utils.functional import Promise
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# Alliance Auth (External Libs)
from app_utils.logging import LoggerAddTag

# AA SRP
from aasrp import __title__
from aasrp.constants import KILLBOARD_DATA
from aasrp.models import (
    FleetType,
    RequestComment,
    Setting,
    SrpLink,
    SrpRequest,
    UserSetting,
)

# Killboard URLs
zkillboard_base_url: str = KILLBOARD_DATA["zKillboard"][  # pylint: disable=invalid-name
    "base_url"
]
evetools_base_url: str = KILLBOARD_DATA["EveTools"][  # pylint: disable=invalid-name
    "base_url"
]
eve_kill_base_url: str = KILLBOARD_DATA["EVE-KILL"][  # pylint: disable=invalid-name
    "base_url"
]

# Killboard regex
zkillboard_base_url_regex: str = KILLBOARD_DATA[  # pylint: disable=invalid-name
    "zKillboard"
]["base_url_regex"]
zkillboard_killmail_url_regex: str = KILLBOARD_DATA[  # pylint: disable=invalid-name
    "zKillboard"
]["killmail_url_regex"]
evetools_base_url_regex: str = KILLBOARD_DATA[  # pylint: disable=invalid-name
    "EveTools"
]["base_url_regex"]
evetools_killmail_url_regex: str = KILLBOARD_DATA[  # pylint: disable=invalid-name
    "EveTools"
]["killmail_url_regex"]
eve_kill_base_url_regex: str = KILLBOARD_DATA[  # pylint: disable=invalid-name
    "EVE-KILL"
]["base_url_regex"]
eve_kill_killmail_url_regex: str = KILLBOARD_DATA[  # pylint: disable=invalid-name
    "EVE-KILL"
]["killmail_url_regex"]

# Initialize a logger with a custom tag for the AA-SRP module
logger = LoggerAddTag(my_logger=get_extension_logger(__name__), prefix=__title__)


def get_mandatory_form_label_text(text: str | Promise) -> str:
    """
    Generate label text for mandatory form fields by appending an asterisk.

    :param text: The label text to modify.
    :type text: str | Promise
    :return: The modified label text with an asterisk.
    :rtype: str
    """

    required_marker_label = _("This field is mandatory")
    required_marker = f'<span aria-label="{required_marker_label}" class="form-required-marker">*</span>'

    return mark_safe(
        f'<span class="form-field-required">{text} {required_marker}</span>'
    )


class SrpLinkForm(ModelForm):
    """
    Form for creating a new SRP link.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for the SrpLinkForm.
        """

        model = SrpLink
        fields = ["srp_name", "fleet_time", "fleet_type", "fleet_doctrine", "aar_link"]
        labels = {
            "srp_name": get_mandatory_form_label_text(text=_("Fleet name")),
            "fleet_time": get_mandatory_form_label_text(text=_("Fleet time")),
            "fleet_type": _("Fleet type (optional)"),
            "fleet_doctrine": get_mandatory_form_label_text(text=_("Doctrine")),
            "aar_link": _("After action report link"),
        }
        querysets = {
            "fleet_type": FleetType.objects.filter(is_enabled=True),
        }
        widgets = {
            "srp_name": forms.TextInput(attrs={"placeholder": _("Fleet name")}),
            "fleet_time": forms.DateTimeInput(
                attrs={"autocomplete": "off", "placeholder": _("Fleet time")}
            ),
            "fleet_type": forms.Select(attrs={"placeholder": _("Fleet type")}),
            "fleet_doctrine": forms.TextInput(attrs={"placeholder": _("Doctrine")}),
            "aar_link": forms.TextInput(
                attrs={"placeholder": _("After action report link")}
            ),
        }


class SrpLinkUpdateForm(ModelForm):
    """
    Form for updating an existing SRP link.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for the SrpLinkUpdateForm.
        """

        model = SrpLink
        fields = ["aar_link"]
        labels = {"aar_link": _("After action report link")}


class SrpRequestForm(ModelForm):
    """
    Form for submitting a new SRP request.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for the SrpRequestForm.
        """

        model = SrpRequest
        fields = ["killboard_link", "additional_info"]
        help_texts = {
            "killboard_link": _(
                "Find your kill mail on {zkillboard_base_url}, {evetools_base_url} or {eve_kill_base_url} and paste the link here."
            ).format(
                zkillboard_base_url=zkillboard_base_url,
                evetools_base_url=evetools_base_url,
                eve_kill_base_url=eve_kill_base_url,
            ),
            "additional_info": _(
                "Please tell us about the circumstances of your untimely demise. "
                "Who was the FC, what doctrine was called, have changes to the fit "
                "been requested and so on. Be as detailed as you can."
            ),
        }
        labels = {
            "killboard_link": get_mandatory_form_label_text(text=_("Killboard link")),
            "additional_info": get_mandatory_form_label_text(
                text=_("Additional information")
            ),
        }
        widgets = {
            "killboard_link": forms.URLInput(
                attrs={"placeholder": _("Killboard link")}
            ),
            "additional_info": forms.Textarea(
                attrs={
                    "placeholder": _("Additional information"),
                    "rows": 10,
                    "cols": 20,
                }
            ),
        }

    def clean_killboard_link(self) -> str:
        """
        Validate and clean the killboard link provided by the user.

        :return: The cleaned killboard link.
        :rtype: str
        :raises forms.ValidationError: If the link is invalid or already exists.
        """

        killboard_link = self.cleaned_data["killboard_link"]

        # Ensure the link ends with a trailing slash if required by the kill board
        for board, data in KILLBOARD_DATA.items():
            if (
                data["requires_trailing_slash"]
                and re.match(data["base_url_regex"], killboard_link)
                and not killboard_link.endswith("/")
            ):
                logger.debug(
                    f"Adding trailing slash to killboard link for {board}: {killboard_link}"
                )

                killboard_link += "/"
                self.cleaned_data["killboard_link"] = killboard_link

        logger.debug(f"Validating killboard link: {killboard_link}")

        # Define regex patterns for accepted kill boards and killmails
        killboard_patterns = [
            zkillboard_base_url_regex,
            evetools_base_url_regex,
            eve_kill_base_url_regex,
        ]
        killmail_patterns = [
            zkillboard_killmail_url_regex,
            evetools_killmail_url_regex,
            eve_kill_killmail_url_regex,
        ]

        # Check if it's a link from one of the accepted kill boards
        if not any(re.match(pattern, killboard_link) for pattern in killboard_patterns):
            logger.debug(
                f"Killboard link does not match any accepted kill board patterns: {killboard_link}"
            )

            raise forms.ValidationError(
                message=_(
                    "Invalid link. Please use {zkillboard_base_url}, {evetools_base_url} or {eve_kill_base_url}"
                ).format(
                    zkillboard_base_url=zkillboard_base_url,
                    evetools_base_url=evetools_base_url,
                    eve_kill_base_url=eve_kill_base_url,
                )
            )

        # Check if it's an actual killmail
        if not any(re.match(pattern, killboard_link) for pattern in killmail_patterns):
            logger.debug(
                f"Killboard link does not match any accepted killmail patterns: {killboard_link}"
            )

            raise forms.ValidationError(
                message=_("Invalid link. Please post a link to a kill mail.")
            )

        # Check if there is already an SRP request for this kill mail
        try:
            killmail_id = SrpRequest.objects.get_kill_id(killboard_link=killboard_link)
        except ValueError as e:
            raise forms.ValidationError(str(e))

        logger.debug(f"Extracted killmail ID: {killmail_id}")

        if SrpRequest.objects.filter(
            killboard_link__icontains=f"/kill/{killmail_id}"
        ).exists():
            logger.debug(
                f"SRP request already exists for killmail ID {killmail_id} and link {killboard_link}"
            )

            raise forms.ValidationError(
                message=_(
                    "There is already an SRP request for this kill mail. "
                    "Please check if you got the right one."
                )
            )

        logger.debug(f"Killboard link validated: {killboard_link}")

        return killboard_link


class SrpRequestPayoutForm(forms.Form):
    """
    Form for changing the payout value of an SRP request.
    """

    value = forms.CharField(label=_("SRP payout value"), max_length=254, required=True)


class SrpRequestRejectForm(ModelForm):
    """
    Form for rejecting an SRP request with a comment.
    """

    class Meta:
        """
        Meta options for the SrpRequestRejectForm.
        """

        model = RequestComment
        fields = ["comment"]
        help_texts = {
            "comment": _("Please provide the reason this SRP request is rejected."),
        }
        labels = {
            "comment": get_mandatory_form_label_text(text=_("Reject reason")),
        }
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 10,
                    "cols": 20,
                    "required": "required",
                }
            ),
        }


class SrpRequestAcceptForm(ModelForm):
    """
    Form for accepting an SRP request with an optional comment.
    """

    class Meta:
        """
        Meta options for the SrpRequestAcceptForm.
        """

        model = RequestComment
        fields = ["comment"]
        help_texts = {
            "comment": _("Leave a comment for the requestor"),
        }
        labels = {
            "comment": _("Comment (optional)"),
        }
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 10,
                    "cols": 20,
                }
            ),
        }


class SrpRequestAcceptRejectedForm(ModelForm):
    """
    Form for accepting a previously rejected SRP request with a comment.
    """

    class Meta:
        """
        Meta options for the SrpRequestAcceptRejectedForm.
        """

        model = RequestComment
        fields = ["comment"]
        help_texts = {
            "comment": _(
                "Please provide the reason why this former "
                "rejected SRP request is now accepted."
            ),
        }
        labels = {
            "comment": get_mandatory_form_label_text(text=_("Comment")),
        }
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 10,
                    "cols": 20,
                    "required": "required",
                }
            ),
        }


class UserSettingsForm(ModelForm):
    """
    Form for managing user-specific settings.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for the UserSettingsForm.
        """

        model = UserSetting
        fields = ["disable_notifications"]
        labels = {
            "disable_notifications": _(
                "Disable notifications. "
                "(Auth and Discord, if a relevant module is installed)"
            ),
        }


class SettingAdminForm(forms.ModelForm):
    """
    Form for managing settings in the admin interface.
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta options for the SettingAdminForm.
        """

        model = Setting
        fields = "__all__"
