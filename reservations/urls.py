from django.urls import path
from . import views

urlpatterns = [
    path('hairdressers/', views.hairdresser_list, name='hairdresser_list'),
    path('reservations/', views.reservation_list, name='reservation_list'),
]
