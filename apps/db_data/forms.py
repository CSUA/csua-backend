from django import forms


class OfficerCreationForm(forms.Form):
    username = forms.CharField(max_length=32)
    photo = forms.ImageField(label="Photo 1", required=False)
    photo_url = forms.CharField(label="Photo 1 URL", required=False)
    photo2 = forms.ImageField(label="Photo 2", required=False)
    photo2_url = forms.CharField(label="Photo 2 URL", required=False)
    blurb = forms.CharField(widget=forms.Textarea, max_length=140)

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data.get("photo"))
        print(cleaned_data.get("photo_url"))
        if (not cleaned_data.get("photo")) == (not cleaned_data.get("photo_url")):
            raise forms.ValidationError(
                "Please specify one of 'Photo 1' or 'Photo 1 URL'"
            )
        if (not cleaned_data.get("photo2")) + (not cleaned_data.get("photo2_url")) == 0:
            raise forms.ValidationError(
                "Please specify up to one of 'Photo 2' or 'Photo 2 URL'"
            )
        return cleaned_data
