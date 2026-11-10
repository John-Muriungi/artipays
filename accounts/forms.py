from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify
import hashlib

from payments.services import normalize_phone

from .models import ArtistProfile

User = get_user_model()


class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150)
    stage_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=16, help_text="Use a Kenyan mobile number.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "full_name", "stage_name", "email", "phone")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        try:
            return normalize_phone(self.cleaned_data["phone"])
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget = forms.HiddenInput()
        self.fields["username"].required = False

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email", "")
        if email:
            base = slugify(email.split("@", 1)[0])[:120] or "artist"
            suffix = hashlib.sha256(email.encode()).hexdigest()[:12]
            cleaned["username"] = f"{base}-{suffix}"
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["full_name"].strip()
        if commit:
            user.save()
            ArtistProfile.objects.create(
                user=user,
                stage_name=self.cleaned_data["stage_name"].strip(),
                phone=self.cleaned_data["phone"].strip(),
            )
        return user


class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = ArtistProfile
        fields = ("stage_name", "phone", "bio", "profile_image")

    def clean_phone(self):
        try:
            return normalize_phone(self.cleaned_data["phone"])
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["full_name"].initial = user.get_full_name()
        self.fields["email"].initial = user.email

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("That email is already in use.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        self.user.first_name = self.cleaned_data["full_name"].strip()
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save(update_fields=["first_name", "email"])
        return profile
