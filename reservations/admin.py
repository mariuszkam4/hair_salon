from typing import Any
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import datetime
from .models import Hairdresser, Service, Reservation, SpecializationChoice
from .forms import ServiceAdminForm, HairdresserAdminForm, ReservationAdminForm

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
    form = ReservationAdminForm
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

admin.site.register(Hairdresser, HairdresserAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(SpecializationChoice)
