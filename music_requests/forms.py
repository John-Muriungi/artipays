from django import forms
from django.core.exceptions import ValidationError


class SongRequestForm(forms.Form):
    requester_name = forms.CharField(max_length=80, required=False)
    song_title = forms.CharField(max_length=150)
    song_artist = forms.CharField(max_length=150)
    message = forms.CharField(max_length=300, required=False, widget=forms.Textarea(attrs={"rows": 2}))
    tip_amount = forms.IntegerField(min_value=0, required=False, initial=0)
    phone_number = forms.CharField(max_length=16)

    def clean_phone_number(self):
        from payments.services import normalize_phone

        try:
            return normalize_phone(self.cleaned_data["phone_number"])
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc


class TipForm(forms.Form):
    requester_name = forms.CharField(max_length=80, required=False)
    amount = forms.IntegerField(min_value=1)
    message = forms.CharField(max_length=300, required=False, widget=forms.Textarea(attrs={"rows": 2}))
    phone_number = forms.CharField(max_length=16)

    def clean_phone_number(self):
        from payments.services import normalize_phone

        try:
            return normalize_phone(self.cleaned_data["phone_number"])
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
