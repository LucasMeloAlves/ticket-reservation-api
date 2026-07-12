from django.contrib import admin

from .models import Event, Reservation


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "location",
        "start_time",
        "price",
        "available_tickets",
        "total_tickets",
        "organizer",
    )
    list_filter = ("location",)
    search_fields = ("name", "location")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "user", "quantity", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("event__name", "user__username")
