"""
Form definitions
"""

# Standard Library
import re

# Django
from django import forms
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# AA SRP
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
zkillboard_base_url: str = KILLBOARD_DATA["zKillboard"]["base_url"]
evetools_base_url: str = KILLBOARD_DATA["EveTools"]["base_url"]
eve_kill_base_url: str = KILLBOARD_DATA["EVE-KILL"]["base_url"]

# Killboard regex
zkillboard_base_url_regex: str = KILLBOARD_DATA["zKillboard"]["base_url_regex"]
zkillboard_killmail_url_regex: str = KILLBOARD_DATA["zKillboard"]["killmail_url_regex"]
evetools_base_url_regex: str = KILLBOARD_DATA["EveTools"]["base_url_regex"]
evetools_killmail_url_regex: str = KILLBOARD_DATA["EveTools"]["killmail_url_regex"]
eve_kill_base_url_regex: str = KILLBOARD_DATA["EVE-KILL"]["base_url_regex"]
eve_kill_killmail_url_regex: str = KILLBOARD_DATA["EVE-KILL"]["killmail_url_regex"]


def get_mandatory_form_label_text(text: str) -> str:
    """
    Label text for mandatory form fields

    :param text:
    :type text:
    :return:
    :rtype:
    """

    required_text = _("This field is mandatory")
    required_marker = (
        f'<span aria-label="{required_text}" class="form-required-marker">*</span>'
    )

    return mark_safe(
        f'<span class="form-field-required">{text} {required_marker}</span>'
    )


class SrpLinkForm(ModelForm):
    """
    New SRP lnk form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
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
    Edit SRP link update form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = SrpLink

        fields = ["aar_link"]
        labels = {"aar_link": _("After action report link")}


class SrpRequestForm(ModelForm):
    """
    SRP request form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
        """

        model = SrpRequest

        fields = ["killboard_link", "additional_info"]
        help_texts = {
            "killboard_link": _(
                f"Find your kill mail on {zkillboard_base_url}, {evetools_base_url} or {eve_kill_base_url} and paste the link here."  # pylint: disable=line-too-long
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

    def clean_killboard_link(self):
        """
        Check if it's a link from one of the accepted kill boards and clean it

        :return:
        :rtype:
        """

        killboard_link = self.cleaned_data["killboard_link"]

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
            raise forms.ValidationError(
                message=_(
                    f"Invalid link. Please use {zkillboard_base_url}, {evetools_base_url} or {eve_kill_base_url}"
                )
            )

        # Check if it's an actual killmail
        if not any(re.match(pattern, killboard_link) for pattern in killmail_patterns):
            raise forms.ValidationError(
                message=_("Invalid link. Please post a link to a kill mail.")
            )

        # Check if there is already an SRP request for this kill mail
        killmail_id = SrpRequest.objects.get_kill_id(killboard_link=killboard_link)

        if SrpRequest.objects.filter(
            killboard_link__icontains=f"/kill/{killmail_id}"
        ).exists():
            raise forms.ValidationError(
                message=_(
                    "There is already an SRP request for this kill mail. "
                    "Please check if you got the right one."
                )
            )

        return killboard_link


class SrpRequestPayoutForm(forms.Form):
    """
    Change payout value
    """

    value = forms.CharField(label=_("SRP payout value"), max_length=254, required=True)


class SrpRequestRejectForm(ModelForm):
    """
    SRP request reject form
    """

    class Meta:
        """
        Meta definitions
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
                    # "placeholder": _("Reject reason"),
                    "required": "required",
                }
            ),
        }


class SrpRequestAcceptForm(ModelForm):
    """
    SRP request accept form
    """

    class Meta:
        """
        Meta definitions
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
                    # "placeholder": _("Reject reason"),
                }
            ),
        }


class SrpRequestAcceptRejectedForm(ModelForm):
    """
    SRP request accept rejected form
    """

    class Meta:
        """
        Meta definitions
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
                    # "placeholder": _("Reject reason"),
                    "required": "required",
                }
            ),
        }


class UserSettingsForm(ModelForm):
    """
    User settings form
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta definitions
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
    Form definitions for the FleetType form in admin
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        Meta
        """

        model = Setting

        fields = "__all__"
        widgets = {"default_embed_color": forms.TextInput(attrs={"type": "color"})}
