from datetime import date, time
from unittest.mock import patch

from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import ArtistProfile
from config.routing import websocket_urlpatterns
from events.models import Event
from music_requests.models import SongRequest, Tip
from payments.models import Transaction

User = get_user_model()


class SongRequestTests(TestCase):
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
            minimum_tip=50,
            status=Event.Status.ACTIVE,
        )

    @patch("music_requests.views.initiate_stk_push")
    def test_request_uses_database_price_and_is_hidden_until_payment(self, initiate):
        initiate.return_value = {"MerchantRequestID": "merchant-1", "CheckoutRequestID": "checkout-1"}
        response = self.client.post(
            reverse("music_requests:create", args=[self.event.public_id]),
            {
                "requester_name": "Fan",
                "song_title": "One Dance",
                "song_artist": "Drake",
                "message": "",
                "tip_amount": "100",
                "phone_number": "0712345678",
                "amount": "1",
            },
        )
        self.assertEqual(response.status_code, 302)
        song_request = SongRequest.objects.get()
        payment = Transaction.objects.get()
        self.assertEqual(payment.amount, 300)
        self.assertEqual(song_request.amount, 200)
        self.assertEqual(song_request.status, SongRequest.Status.AWAITING_PAYMENT)
        self.client.force_login(self.artist)
        self.assertNotContains(self.client.get(reverse("music_requests:list")), "One Dance")

    @patch("music_requests.views.initiate_stk_push")
    def test_closed_event_rejects_request_and_other_artist_has_no_access(self, initiate):
        self.event.status = Event.Status.COMPLETED
        self.event.save()
        response = self.client.post(
            reverse("music_requests:create", args=[self.event.public_id]),
            {
                "song_title": "Track",
                "song_artist": "Singer",
                "phone_number": "0712345678",
            },
        )
        self.assertEqual(response.status_code, 200)
        initiate.assert_not_called()
        self.assertFalse(SongRequest.objects.exists())
        self.client.force_login(self.other)
        self.assertEqual(
            self.client.post(
                reverse("music_requests:status", args=["00000000-0000-0000-0000-000000000001"]),
                {"action": "accept"},
            ).status_code,
            404,
        )

    def test_invalid_phone_is_rejected(self):
        response = self.client.post(
            reverse("music_requests:create", args=[self.event.public_id]),
            {
                "song_title": "Track",
                "song_artist": "Singer",
                "phone_number": "not-a-phone",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SongRequest.objects.exists())

    @patch("music_requests.views.initiate_stk_push")
    def test_tip_uses_server_minimum_and_is_recorded_pending(self, initiate):
        initiate.return_value = {"MerchantRequestID": "merchant-tip", "CheckoutRequestID": "checkout-tip"}
        response = self.client.post(
            reverse("music_requests:tip", args=[self.event.public_id]),
            {
                "requester_name": "Fan",
                "amount": "100",
                "message": "Great set",
                "phone_number": "0712345678",
            },
        )
        self.assertEqual(response.status_code, 302)
        tip = Tip.objects.get()
        payment = Transaction.objects.get()
        self.assertEqual(tip.amount, 100)
        self.assertFalse(tip.paid)
        self.assertEqual(payment.amount, 100)
        self.assertEqual(payment.transaction_type, Transaction.Type.TIP)

    @patch("music_requests.views.initiate_stk_push")
    def test_tip_below_event_minimum_is_rejected(self, initiate):
        response = self.client.post(
            reverse("music_requests:tip", args=[self.event.public_id]),
            {"amount": "49", "phone_number": "0712345678"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tip.objects.exists())
        initiate.assert_not_called()

    def test_artist_can_advance_paid_request_status(self):
        song_request = SongRequest.objects.create(
            event=self.event,
            artist=self.artist,
            song_title="One Dance",
            song_artist="Drake",
            amount=200,
            status=SongRequest.Status.PENDING,
        )
        self.client.force_login(self.artist)
        response = self.client.post(
            reverse("music_requests:status", args=[song_request.public_id]),
            {"action": "accept"},
        )
        self.assertRedirects(response, reverse("music_requests:list"))
        song_request.refresh_from_db()
        self.assertEqual(song_request.status, SongRequest.Status.ACCEPTED)

    async def test_authenticated_artist_receives_paid_request_websocket_notice(self):
        communicator = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns), "/ws/artist/requests/"
        )
        communicator.scope["user"] = self.artist
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await get_channel_layer().group_send(
            f"artist_{self.artist.pk}",
            {"type": "artist.notification", "payload": {"type": "paid_request"}},
        )
        self.assertEqual(
            await communicator.receive_json_from(), {"type": "paid_request"}
        )
        await communicator.disconnect()

    async def test_anonymous_websocket_connection_is_rejected(self):
        from django.contrib.auth.models import AnonymousUser

        communicator = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns), "/ws/artist/requests/"
        )
        communicator.scope["user"] = AnonymousUser()
        connected, close_code = await communicator.connect()
        self.assertFalse(connected)
        self.assertEqual(close_code, 4401)

    @patch("music_requests.views.initiate_stk_push")
    def test_song_request_allows_omitted_optional_tip(self, initiate):
        initiate.return_value = {"MerchantRequestID": "merchant-no-tip", "CheckoutRequestID": "checkout-no-tip"}
        response = self.client.post(
            reverse("music_requests:create", args=[self.event.public_id]),
            {
                "song_title": "Track",
                "song_artist": "Singer",
                "phone_number": "0712345678",
            },
        )
        self.assertEqual(response.status_code, 302)
        song_request = SongRequest.objects.get()
        self.assertEqual(song_request.tip_amount, 0)
        self.assertEqual(Transaction.objects.get().amount, 200)
