from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Event, Reservation

User = get_user_model()


# Test automatici: controllano che l'API si comporti come previsto.
# Si lanciano con:  python manage.py test
class TicketingAPITests(APITestCase):

    # Prima di ogni test creo utenti e un evento di prova.
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="org", password="pass12345", role="ORGANIZER"
        )
        self.user = User.objects.create_user(
            username="alice", password="pass12345", role="USER"
        )
        self.other = User.objects.create_user(
            username="bob", password="pass12345", role="USER"
        )
        now = timezone.now()
        self.event = Event.objects.create(
            name="Test Event",
            location="Firenze",
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=2),
            price="10.00",
            total_tickets=10,
            organizer=self.organizer,
        )

    # Aiuto: faccio il login e mi tengo il token.
    def _login(self, username, password="pass12345"):
        res = self.client.post(
            reverse("login"), {"username": username, "password": password}
        )
        self.assertEqual(res.status_code, 200, res.data)
        return res.data["access"]

    # Aiuto: allego il token alle prossime richieste.
    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # --- Accesso pubblico --------------------------------------------------
    def test_events_list_is_public(self):
        # Senza login devo comunque poter vedere gli eventi.
        self.client.credentials()
        res = self.client.get(reverse("event-list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["count"], 1)

    def test_availability_is_public(self):
        # La disponibilita' posti e' pubblica.
        res = self.client.get(reverse("event-availability", args=[self.event.id]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["available_tickets"], 10)

    # --- Permessi per ruolo -----------------------------------------------
    def test_standard_user_cannot_create_event(self):
        # Un utente normale NON puo' creare eventi -> deve ricevere 403.
        self._auth(self._login("alice"))
        res = self.client.post(
            reverse("event-list"),
            {
                "name": "X",
                "location": "Y",
                "start_time": timezone.now() + timedelta(days=2),
                "end_time": timezone.now() + timedelta(days=2, hours=1),
                "total_tickets": 5,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_can_create_event(self):
        # Un organizzatore invece puo' -> deve ricevere 201.
        self._auth(self._login("org"))
        res = self.client.post(
            reverse("event-list"),
            {
                "name": "New",
                "location": "Y",
                "start_time": timezone.now() + timedelta(days=2),
                "end_time": timezone.now() + timedelta(days=2, hours=1),
                "total_tickets": 5,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # --- Prenotazioni e disponibilita' ------------------------------------
    def test_reservation_decrements_availability(self):
        # Prenotando 3 biglietti su 10, ne devono restare 7.
        self._auth(self._login("alice"))
        res = self.client.post(
            reverse("reservation-list"),
            {"event": self.event.id, "quantity": 3},
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.event.refresh_from_db()
        self.assertEqual(self.event.available_tickets, 7)

    def test_overbooking_is_rejected(self):
        # Non posso prenotare piu' biglietti di quelli disponibili.
        self._auth(self._login("alice"))
        res = self.client.post(
            reverse("reservation-list"),
            {"event": self.event.id, "quantity": 999},
        )
        self.assertEqual(res.status_code, 400)

    def test_cancel_restores_tickets(self):
        # Annullando la prenotazione, i biglietti tornano disponibili.
        self._auth(self._login("alice"))
        r = self.client.post(
            reverse("reservation-list"),
            {"event": self.event.id, "quantity": 2},
        )
        rid = r.data["id"]
        res = self.client.post(reverse("reservation-cancel", args=[rid]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["status"], "CANCELLED")
        self.event.refresh_from_db()
        self.assertEqual(self.event.available_tickets, 10)

    # --- Azione vietata: non posso toccare le prenotazioni degli altri -----
    def test_user_cannot_cancel_others_reservation(self):
        self._auth(self._login("alice"))
        r = self.client.post(
            reverse("reservation-list"),
            {"event": self.event.id, "quantity": 1},
        )
        rid = r.data["id"]
        # Bob prova ad annullare la prenotazione di Alice -> deve fallire.
        self._auth(self._login("bob"))
        res = self.client.post(reverse("reservation-cancel", args=[rid]))
        self.assertIn(res.status_code, (403, 404))

    def test_only_organizer_sees_attendees(self):
        # La lista partecipanti la vede solo l'organizzatore, non un utente normale.
        self._auth(self._login("alice"))
        self.client.post(
            reverse("reservation-list"),
            {"event": self.event.id, "quantity": 1},
        )
        res = self.client.get(reverse("event-attendees", args=[self.event.id]))
        self.assertEqual(res.status_code, 403)  # utente normale: vietato
        self._auth(self._login("org"))
        res = self.client.get(reverse("event-attendees", args=[self.event.id]))
        self.assertEqual(res.status_code, 200)  # organizzatore: permesso
        self.assertEqual(res.data["count"], 1)
