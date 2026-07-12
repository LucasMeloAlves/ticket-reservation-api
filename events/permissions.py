from rest_framework import permissions


# Regola per gli eventi:
# - chiunque puo' LEGGERE gli eventi (anche senza login)
# - solo organizzatori/admin possono CREARE eventi
# - solo chi ha creato l'evento (o un admin) puo' MODIFICARLO o CANCELLARLO
class IsOrganizerOrReadOnly(permissions.BasePermission):
    message = "Solo gli organizzatori possono creare o modificare gli eventi."

    # Controllo generale sulla richiesta (vale per la lista e la creazione).
    def has_permission(self, request, view):
        # I metodi "sicuri" (GET, HEAD, OPTIONS) sono sempre permessi.
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and user.is_organizer)

    # Controllo sul singolo evento (per modifica/cancellazione).
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        # Ok se sei admin oppure se sei tu che hai creato l'evento.
        return bool(user and (user.is_admin or obj.organizer_id == user.id))


# Regola per le prenotazioni:
# ognuno puo' vedere e gestire solo le PROPRIE prenotazioni (gli admin tutte).
class IsReservationOwner(permissions.BasePermission):
    message = "Puoi accedere solo alle tue prenotazioni."

    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(user and (user.is_admin or obj.user_id == user.id))
