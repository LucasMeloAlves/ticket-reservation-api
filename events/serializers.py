from rest_framework import serializers

from .models import Event, Reservation


# I serializer trasformano gli oggetti Python in JSON (e viceversa),
# e controllano che i dati in arrivo siano validi.


# Serializer per gli eventi.
class EventSerializer(serializers.ModelSerializer):
    # Mostro il nome dell'organizzatore invece del suo id.
    organizer = serializers.ReadOnlyField(source="organizer.username")
    is_sold_out = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "description",
            "location",
            "start_time",
            "end_time",
            "price",
            "total_tickets",
            "available_tickets",
            "is_sold_out",
            "organizer",
            "created_at",
        ]
        # Questi campi non si possono impostare dall'esterno.
        read_only_fields = ["available_tickets", "organizer", "created_at"]

    # Controllo di buon senso: la fine dell'evento deve venire dopo l'inizio.
    def validate(self, attrs):
        start = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end = attrs.get("end_time", getattr(self.instance, "end_time", None))
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_time": "La data di fine deve essere dopo quella di inizio."}
            )
        return attrs


# Versione ridotta usata per la lista dei partecipanti a un evento.
class AttendeeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Reservation
        fields = ["id", "user", "quantity", "status", "created_at"]


# Serializer per le prenotazioni.
class ReservationSerializer(serializers.ModelSerializer):
    event_name = serializers.ReadOnlyField(source="event.name")
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Reservation
        fields = [
            "id",
            "event",
            "event_name",
            "user",
            "quantity",
            "status",
            "created_at",
            "updated_at",
        ]
        # L'utente e lo stato li decide il server, non chi fa la richiesta.
        read_only_fields = ["user", "status", "created_at", "updated_at"]

    # La quantita' deve essere almeno 1.
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Devi prenotare almeno 1 biglietto.")
        return value

    # Quando creo una prenotazione, controllo che ci siano abbastanza biglietti.
    def validate(self, attrs):
        if self.instance is None:  # None = sto creando, non modificando
            event = attrs["event"]
            quantity = attrs.get("quantity", 1)
            if event.available_tickets < quantity:
                raise serializers.ValidationError(
                    {
                        "quantity": (
                            f"Sono disponibili solo {event.available_tickets} "
                            f"biglietti per '{event.name}'."
                        )
                    }
                )
        return attrs
