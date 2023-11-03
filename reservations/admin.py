from django.contrib import admin
from .models import Hairdresser, Service, Reservation, SpecializationChoice

admin.site.register(Hairdresser)
admin.site.register(Service)
admin.site.register(Reservation)
admin.site.register(SpecializationChoice)
