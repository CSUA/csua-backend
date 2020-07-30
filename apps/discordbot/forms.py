import re
from django import forms

discord_tag_regex = re.compile(r".{2,32}#[0-9]{4}")


class DiscordRegisterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "pnunez@berkeley.edu"})
    )
    discord_tag = forms.CharField(
        label="Discord Tag",
        widget=forms.TextInput(attrs={"placeholder": "pnunez#1337"}),
    )
    # csua_username = forms.CharField(
    #     label="CSUA Username",
    #     required=False,
    #     widget=forms.TextInput(attrs={"placeholder": "(Optional) pnunez"}),
    # )

    def clean(self):
        cleaned_data = super().clean()

        errors = []
        email = cleaned_data.get("email")
        if not email.endswith("@berkeley.edu"):
            errors.append(
                "You must use your @berkeley.edu email. "
                "If you do not yet have one, please contact "
                "jonathan@csua.berkeley.edu."
            )

        if not discord_tag_regex.fullmatch(cleaned_data.get("discord_tag")):
            errors.append("Invalid Discord tag")

        if DiscordRegisteredUser.objects.filter(email=email).exists():
            errors.append("Email already registered")
        if DiscordRegisteredUser.objects.filter(discord_tag=discord_tag).exists():
            errors.append("Discord Tag already registered")

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data
