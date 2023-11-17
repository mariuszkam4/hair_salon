from django.contrib import admin, messages
from django.utils.html import format_html
from django.core.exceptions import ValidationError
import datetime
from .models import Hairdresser, Service, Reservation, SpecializationChoice
from .forms import ServiceAdminForm, HairdresserAdminForm, ReservationForm
import logging

logger = logging.getLogger(__name__)

class HairdresserAdmin(admin.ModelAdmin):
    form = HairdresserAdminForm
    list_display = ['name', 'list_specializations']
    search_fields = ['name']

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css',),
        }
        js = ('/admin/jsi18n',)

    def list_specializations(self, obj):
        return ", ".join([s.get_specialization_display() for s in obj.specialization.all()])
    list_specializations.short_description = 'Specializations'

class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ('name', 'cost', 'duration', 'list_specializations')
    list_filter = ('specializations',)
    search_fields = ('name',)
    ordering = ('name',)

    def list_specializations(self, obj):
        return ", ".join([spec.get_specialization_display() for spec in obj.specializations.all()])
    list_specializations.short_description = "Specializations"

class ReservationAdmin(admin.ModelAdmin):
    form = ReservationForm
    list_display = ('hairdresser', 'day_column', 'time_column', 'service')

    def day_column(self, obj):
        return obj.start_time.strftime('%d-%m-%Y')
    day_column.admin_order_field = 'start_time'
    day_column.short_description = 'Dzień'

    def time_column(self, obj):
        return format_html('{} - {}',
                           obj.start_time.strftime('%H:%M'),
                           obj.end_time.strftime('%H:%M'))
    time_column.short_description = 'Godzina'

    def get_queryset(self, request): 
        return super().get_queryset(request).filter(start_time__gte=datetime.date.today())
    
    def save_model(self, request, obj, form, change):
        print("save_model w ReservationAdmin")
        print(f"POST data w ReservationAdmin: {request.POST}")
        print(f"Form errors: {form.errors}")
        print(f"Form cleaned data: {form.cleaned_data}")
        print(f"Reservation object before save: {obj}")

        if not obj.end_time and obj.start_time and obj.service:
            obj.end_time = obj.start_time + obj.service.duration
            print(f"Automatically set end_time: {obj.end_time}")

        # Sprawdzenie kolizji rezerwacji
        conflicting_reservations = Reservation.objects.filter(
            hairdresser=obj.hairdresser,
            start_time__lt=obj.end_time,
            end_time__gt=obj.start_time,
        ).exclude(pk=obj.pk)

        if conflicting_reservations.exists():
            messages.add_message(request, messages.ERROR, "Podany termin jest już zajęty, proszę wybrać inny termin.")
            print("Konflikt rezerwacji!")
        else:
            super().save_model(request, obj, form, change)
            print("Rezerwacja zapisana pomyślnie")

admin.site.register(Hairdresser, HairdresserAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(SpecializationChoice)
