# coding=utf-8

"""
Form definitions
"""

from django import forms
from django.utils.translation import ugettext_lazy as _


class AaSrpLinkForm(forms.Form):
    srp_name = forms.CharField(required=True, label=_("Fleet Name"))
    fleet_time = forms.DateTimeField(required=True, label=_("Fleet Time"))
    fleet_doctrine = forms.CharField(required=True, label=_("Fleet Doctrine"))
    aar_link = forms.CharField(required=False, label=_("AAR Link"))


class AaSrpLinkUpdateForm(forms.Form):
    aar_link = forms.CharField(required=True, label=_("After Action Report Link"))


class AaSrpRequestForm(forms.Form):
    additional_info = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5, "cols": 20}),
        required=True,
        label=_("Additional Info"),
    )

    killboard_link = forms.CharField(
        label=_("zKillboard Link"), max_length=254, required=True
    )

    def clean_killboard_link(self):
        data = self.cleaned_data["killboard_link"]

        if "zkillboard.com" not in data:
            raise forms.ValidationError(_("Invalid Link. Please use zKillboard.com"))

        return data
