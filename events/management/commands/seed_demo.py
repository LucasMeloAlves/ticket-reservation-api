"""Riempie il database con dati di prova: account, eventi e prenotazioni.

Si lancia con:  python manage.py seed_demo

Si puo' rilanciare quante volte vuoi: cancella prima i vecchi dati e li ricrea.
Le credenziali qui sotto sono solo per la valutazione (nessun dato reale).
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event, Reservation

User = get_user_model()


class Command(BaseCommand):
    help = "Crea account, eventi e prenotazioni di prova."

    def handle(self, *args, **options):
        self.stdout.write("Cancello i vecchi dati di prova...")
        Reservation.objects.all().delete()
        Event.objects.all().delete()
        User.objects.all().delete()

        # --- Account demo (uno per ogni ruolo) -------------------------------
        admin = User.objects.create_superuser(
            username="admin_demo",
            email="admin_demo@example.com",
            password="admin12345",
        )
        admin.role = "ADMIN"
        admin.save(update_fields=["role"])

        organizer = User.objects.create_user(
            username="organizer_demo",
            email="organizer_demo@example.com",
            password="organizer12345",
            role="ORGANIZER",
            phone_number="+39 055 0000001",
        )

        user = User.objects.create_user(
            username="user_demo",
            email="user_demo@example.com",
            password="user12345",
            role="USER",
            phone_number="+39 055 0000002",
        )

        # Un secondo utente normale, comodo per provare le azioni non permesse.
        other = User.objects.create_user(
            username="user2_demo",
            email="user2_demo@example.com",
            password="user12345",
            role="USER",
        )

        # --- Eventi demo -----------------------------------------------------
        now = timezone.now()
        events_data = [
            {
                "name": "Firenze Jazz Night",
                "description": "An evening of live jazz in the heart of Florence.",
                "location": "Teatro Verdi, Firenze",
                "start_time": now + timedelta(days=14, hours=20),
                "end_time": now + timedelta(days=14, hours=23),
                "price": "25.00",
                "total_tickets": 120,
            },
            {
                "name": "Tech Conference 2026",
                "description": "Talks and workshops on backend engineering and APIs.",
                "location": "Palazzo dei Congressi, Firenze",
                "start_time": now + timedelta(days=30, hours=9),
                "end_time": now + timedelta(days=31, hours=18),
                "price": "80.00",
                "total_tickets": 300,
            },
            {
                "name": "Contemporary Art Expo",
                "description": "A showcase of works by emerging local artists.",
                "location": "Downtown Gallery, Firenze",
                "start_time": now + timedelta(days=7, hours=10),
                "end_time": now + timedelta(days=9, hours=18),
                "price": "12.00",
                "total_tickets": 200,
            },
            {
                "name": "Marathon Charity Run",
                "description": "A 10km charity run across the city centre.",
                "location": "Piazza della Signoria, Firenze",
                "start_time": now + timedelta(days=45, hours=8),
                "end_time": now + timedelta(days=45, hours=13),
                "price": "0.00",
                "total_tickets": 500,
            },
        ]

        events = []
        for data in events_data:
            events.append(Event.objects.create(organizer=organizer, **data))

        # --- Prenotazioni demo ----------------------------------------------
        self._reserve(user, events[0], 2)
        self._reserve(user, events[1], 1)
        self._reserve(other, events[0], 3)

        self.stdout.write(self.style.SUCCESS("Dati di prova creati con successo."))
        self.stdout.write("Account:")
        self.stdout.write("  admin_demo     / admin12345      (ADMIN)")
        self.stdout.write("  organizer_demo / organizer12345  (ORGANIZER)")
        self.stdout.write("  user_demo      / user12345       (USER)")
        self.stdout.write("  user2_demo     / user12345       (USER)")

    # Piccolo aiuto: crea una prenotazione e aggiorna i posti disponibili.
    @staticmethod
    def _reserve(user, event, quantity):
        Reservation.objects.create(user=user, event=event, quantity=quantity)
        event.available_tickets -= quantity
        event.save(update_fields=["available_tickets"])
