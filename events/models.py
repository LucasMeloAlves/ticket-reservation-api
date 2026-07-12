from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# Un evento per cui si possono prenotare biglietti.
class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tickets = models.PositiveIntegerField(default=0)      # biglietti totali
    available_tickets = models.PositiveIntegerField(default=0)  # biglietti ancora liberi

    # Chi ha creato l'evento. E' un collegamento all'utente (relazione 1).
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]  # mostra prima gli eventi piu' vicini nel tempo

    # Quando creo un evento nuovo, all'inizio i biglietti liberi
    # sono uguali a quelli totali.
    def save(self, *args, **kwargs):
        if self._state.adding and not self.available_tickets:
            self.available_tickets = self.total_tickets
        super().save(*args, **kwargs)

    # "L'evento e' esaurito?" -> True se non ci sono piu' biglietti
    @property
    def is_sold_out(self):
        return self.available_tickets <= 0

    def __str__(self):
        return f"{self.name} @ {self.location}"


# Una prenotazione: un utente prenota dei biglietti per un evento.
class Reservation(models.Model):

    # Stato della prenotazione: attiva o annullata.
    STATUS_CHOICES = [
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    # A quale evento si riferisce (relazione 2).
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    # Chi ha fatto la prenotazione (relazione 3).
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    # Quanti biglietti (almeno 1).
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="CONFIRMED",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # le piu' recenti per prime

    def __str__(self) -> str:
        return (
            f"{self.user.username} - {self.quantity}x {self.event.name} "
            f"[{self.status}]"
        )
