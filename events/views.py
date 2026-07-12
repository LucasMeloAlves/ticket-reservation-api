from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, Reservation
from .permissions import IsOrganizerOrReadOnly, IsReservationOwner
from .serializers import AttendeeSerializer, EventSerializer, ReservationSerializer


# --- Eventi ---

class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]

    def get_queryset(self):
        qs = Event.objects.all()
        search = self.request.query_params.get("search")
        location = self.request.query_params.get("location")
        if search:
            qs = qs.filter(name__icontains=search)
        if location:
            qs = qs.filter(location__icontains=location)
        return qs

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsOrganizerOrReadOnly]


class EventAvailabilityView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        return Response({
            "event": event.name,
            "total_tickets": event.total_tickets,
            "available_tickets": event.available_tickets,
            "is_sold_out": event.is_sold_out,
        })


class EventAttendeesView(generics.ListAPIView):
    serializer_class = AttendeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs["pk"])
        user = self.request.user
        if not (user.is_admin or event.organizer_id == user.id):
            raise PermissionDenied("Solo l'organizzatore puo' vedere i partecipanti.")
        return event.reservations.filter(status="CONFIRMED")


# --- Prenotazioni ---

class ReservationListCreateView(generics.ListCreateAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        with transaction.atomic():
            event = serializer.validated_data["event"]
            quantity = serializer.validated_data.get("quantity", 1)
            if event.available_tickets < quantity:
                raise ValidationError({"quantity": "Biglietti non sufficienti."})
            serializer.save(user=self.request.user)
            event.available_tickets -= quantity
            event.save()


class ReservationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated, IsReservationOwner]

    def get_queryset(self):
        return Reservation.objects.all()

    def perform_update(self, serializer):
        with transaction.atomic():
            reservation = serializer.instance
            new_quantity = serializer.validated_data.get("quantity", reservation.quantity)
            if new_quantity > reservation.quantity:
                raise ValidationError({"quantity": "Non puoi aumentare i biglietti."})
            if new_quantity < reservation.quantity:
                event = reservation.event
                event.available_tickets += reservation.quantity - new_quantity
                event.save()
            serializer.save()

    def perform_destroy(self, instance):
        with transaction.atomic():
            if instance.status == "CONFIRMED":
                event = instance.event
                event.available_tickets += instance.quantity
                event.save()
            instance.delete()


class ReservationCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReservationOwner]

    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        self.check_object_permissions(request, reservation)
        if reservation.status == "CANCELLED":
            return Response({"detail": "Prenotazione gia' annullata."},
                            status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            event = reservation.event
            event.available_tickets += reservation.quantity
            event.save()
            reservation.status = "CANCELLED"
            reservation.save()
        return Response(ReservationSerializer(reservation).data)
