from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import ArtistProfile

User = get_user_model()


class RegistrationTests(TestCase):
    def test_registration_creates_artist_and_redirects_to_login_without_authentication(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "Jane Doe",
                "stage_name": "DJ Jane",
                "email": "jane@example.com",
                "phone": "0712345678",
                "password1": "Use-a-Strong-Pass-927!",
                "password2": "Use-a-Strong-Pass-927!",
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(email="jane@example.com")
        self.assertTrue(user.check_password("Use-a-Strong-Pass-927!"))
        self.assertFalse("_auth_user_id" in self.client.session)
        self.assertEqual(user.artistprofile.stage_name, "DJ Jane")
        self.assertEqual(user.artistprofile.phone, "254712345678")

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user("first", email="same@example.com", password="Strong-password-24!")
        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "Another Artist",
                "stage_name": "Another",
                "email": "SAME@example.com",
                "phone": "0712345678",
                "password1": "Use-a-Strong-Pass-927!",
                "password2": "Use-a-Strong-Pass-927!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_password_is_rejected(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "Jane Doe",
                "stage_name": "DJ Jane",
                "email": "jane@example.com",
                "phone": "0712345678",
                "password1": "password",
                "password2": "password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="jane@example.com").exists())

    def test_login_redirects_to_dashboard(self):
        user = User.objects.create_user(
            "loginartist", email="artist@example.com", password="Strong-password-24!"
        )
        ArtistProfile.objects.create(user=user, stage_name="The Artist", phone="254712345678")
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "artist@example.com", "password": "Strong-password-24!"},
        )
        self.assertRedirects(response, reverse("dashboard:home"))
