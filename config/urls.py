"""Elenco degli indirizzi (URL) principali del progetto."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


# Pagina iniziale: se apri l'indirizzo base ("/") vedi un riepilogo
# degli endpoint disponibili. Serve solo a far capire che l'API e' viva.
def api_root(request):
    return JsonResponse(
        {
            "service": "Ticket Reservation API",
            "status": "ok",
            "docs": "See README.md for the full endpoint documentation.",
            "endpoints": {
                "auth": "/api/auth/",
                "events": "/api/events/",
                "reservations": "/api/reservations/",
                "admin": "/admin/",
            },
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),              # pagina iniziale "/"
    path("admin/", admin.site.urls),                  # pannello di amministrazione
    path("api/auth/", include("accounts.urls")),      # registrazione e login
    path("api/", include("events.urls")),             # eventi e prenotazioni
]
