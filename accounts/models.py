from django.contrib.auth.models import AbstractUser
from django.db import models


# Utente personalizzato: parto da quello di Django (AbstractUser) e aggiungo
# il ruolo, così posso decidere chi puo' fare cosa nell'app.
class User(AbstractUser):

    # I tre ruoli possibili:
    # - USER      = utente normale, gestisce solo le sue prenotazioni
    # - ORGANIZER = puo' creare eventi e vedere chi si e' prenotato
    # - ADMIN     = accesso completo (anche al pannello di amministrazione)
    ROLE_CHOICES = [
        ("USER", "User"),
        ("ORGANIZER", "Organizer"),
        ("ADMIN", "Admin"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="USER")
    phone_number = models.CharField(max_length=20, blank=True)

    # Scorciatoia comoda: "questo utente e' un organizzatore?"
    # (anche lo staff di Django viene considerato organizzatore)
    @property
    def is_organizer(self):
        return self.role == "ORGANIZER" or self.is_staff

    # Scorciatoia comoda: "questo utente e' un amministratore?"
    @property
    def is_admin(self):
        return self.role == "ADMIN" or self.is_staff or self.is_superuser

    # Come viene mostrato l'utente (es. nel pannello admin)
    def __str__(self):
        return f"{self.username} ({self.role})"
