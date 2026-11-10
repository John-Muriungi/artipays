from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import ArtistProfile
from events.models import Event

User = get_user_model()


class EventTests(TestCase):
    def setUp(self):
        self.artist = User.objects.create_user("dj", email="dj@example.com", password="Strong-password-24!")
        ArtistProfile.objects.create(user=self.artist, stage_name="DJ Test", phone="254712345678")
        self.other = User.objects.create_user("other", email="other@example.com", password="Strong-password-24!")
        ArtistProfile.objects.create(user=self.other, stage_name="Other DJ", phone="254712345679")
        self.event = Event.objects.create(
            artist=self.artist,
            name="Friday Live",
            event_date=date(2027, 5, 1),
            start_time=time(20, 0),
            song_request_price=200,
            status=Event.Status.ACTIVE,
        )

    def test_artist_creates_event_with_individual_price(self):
        self.client.force_login(self.artist)
        response = self.client.post(
            reverse("events:create"),
            {
                "name": "Saturday Set",
                "event_date": "2027-05-02",
                "start_time": "21:00",
                "song_request_price": 500,
                "minimum_tip": 50,
                "status": Event.Status.ACTIVE,
            },
        )
        self.assertRedirects(response, reverse("events:detail", args=[self.event.pk + 1]))
        self.assertEqual(Event.objects.get(name="Saturday Set").song_request_price, 500)

    def test_artist_cannot_read_or_edit_another_artists_event(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("events:detail", args=[self.event.pk])).status_code, 404)
        response = self.client.post(
            reverse("events:edit", args=[self.event.pk]),
            {"name": "Stolen", "event_date": "2027-05-01", "start_time": "20:00", "song_request_price": 1},
        )
        self.assertEqual(response.status_code, 404)
        self.event.refresh_from_db()
        self.assertEqual(self.event.name, "Friday Live")

    def test_public_page_and_qr_code(self):
        response = self.client.get(self.event.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DJ Test")
        self.client.force_login(self.artist)
        qr_response = self.client.get(reverse("events:qr_image", args=[self.event.pk]))
        self.assertEqual(qr_response.status_code, 200)
        self.assertEqual(qr_response["Content-Type"], "image/png")

    def test_closed_event_public_page_disables_payment_actions(self):
        self.event.status = Event.Status.COMPLETED
        self.event.save()
        response = self.client.get(self.event.get_absolute_url())
        self.assertContains(response, "Requests are closed")
