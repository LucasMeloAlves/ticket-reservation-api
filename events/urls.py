from django.urls import path

from .views import (
    EventAttendeesView,
    EventAvailabilityView,
    EventDetailView,
    EventListCreateView,
    ReservationCancelView,
    ReservationDetailView,
    ReservationListCreateView,
)

urlpatterns = [
    # Events
    path("events/", EventListCreateView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path(
        "events/<int:pk>/availability/",
        EventAvailabilityView.as_view(),
        name="event-availability",
    ),
    path(
        "events/<int:pk>/attendees/",
        EventAttendeesView.as_view(),
        name="event-attendees",
    ),
    # Reservations
    path(
        "reservations/",
        ReservationListCreateView.as_view(),
        name="reservation-list",
    ),
    path(
        "reservations/<int:pk>/",
        ReservationDetailView.as_view(),
        name="reservation-detail",
    ),
    path(
        "reservations/<int:pk>/cancel/",
        ReservationCancelView.as_view(),
        name="reservation-cancel",
    ),
]
