from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Hairdresser, Service, Reservation
from .forms import ReservationForm

def reservation_list(request):
    reservations = Reservation.objects.all()
    return render(request, 'reservation_list.html', {'reservations': reservations})
