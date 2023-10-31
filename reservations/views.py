from django.shortcuts import render
from .models import Hairdresser, Service, Reservation

def hairdresser_list(request):
    haidressers = Hairdresser.objects.all()
    return render(request, 'hairdresser_list.html', {'hairdressers': haidressers})

def service_list(request):
    services = Service.objects.all()
    return render(request, 'service_list.html', {'services': services})

def reservation_list(request):
    reservations = Reservation.objects.all()
    return render(request, 'reservations_list.html', {'reservations': reservations})
