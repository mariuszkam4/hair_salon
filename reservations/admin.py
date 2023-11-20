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
    list_display = ('hairdresser', 'service', 'start_date', 'start_time', 'end_time')

    def day_column(self, obj):
        return obj.start_date.strftime('%d-%m-%Y')
    day_column.admin_order_field = 'start_date'
    day_column.short_description = 'Dzień'

    def time_column(self, obj):
        start_time_str = obj.start_time.strftime('%H:%M') if obj.start_time else ''
        end_time_str = obj.end_time.strftime('%H:%M') if obj.end_time else ''
        return format_html('{} - {}', start_time_str, end_time_str)
    time_column.short_description = 'Godzina'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(start_date__gte=datetime.date.today())

    def save_model(self, request, obj, form, change):
        # Obliczanie end_time tylko wtedy, gdy nie jest już ustalone
        if not obj.end_time and obj.start_time and obj.service:
            end_datetime = datetime.combine(obj.start_date, obj.start_time) + obj.service.duration
            obj.end_time = end_datetime.time()

        # Sprawdzenie konfliktów terminów
        conflicting_reservations = Reservation.objects.filter(
            hairdresser=obj.hairdresser,
            start_date=obj.start_date,
            start_time__lt=obj.end_time,
            end_time__gt=obj.start_time,
        ).exclude(pk=obj.pk)

        if conflicting_reservations.exists():
            messages.add_message(request, messages.ERROR, "Podany termin jest już zajęty, proszę wybrać inny termin.")
        else:
            super().save_model(request, obj, form, change)
            
admin.site.register(Hairdresser, HairdresserAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(SpecializationChoice)
