from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django_ratelimit.decorators import ratelimit

from .forms import ProfileForm, RegistrationForm


class ArtistAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

    def clean(self):
        email = self.cleaned_data.get("username")
        if email:
            user = get_user_model().objects.filter(email__iexact=email).first()
            self.cleaned_data["username"] = user.get_username() if user else email
        return super().clean()


@method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True), name="dispatch")
class ArtistLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = ArtistAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard:home")


@method_decorator(ratelimit(key="ip", rate="10/h", method="POST", block=True), name="dispatch")
class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect("accounts:login")
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class ProfileView(View):
    template_name = "accounts/profile.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {"form": ProfileForm(instance=request.user.artistprofile, user=request.user)},
        )

    def post(self, request):
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.artistprofile,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
        return render(request, self.template_name, {"form": form})
