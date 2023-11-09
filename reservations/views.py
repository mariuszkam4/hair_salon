from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Hairdresser, Service, Reservation
from .forms import ReservationForm
import logging

logger = logging.getLogger(__name__)

def hairdresser_list(request):
    haidressers = Hairdresser.objects.all()
    return render(request, 'hairdresser_list.html', {'hairdressers': haidressers})

def service_list(request):
    services = Service.objects.all()
    return render(request, 'service_list.html', {'services': services})

def reservation_list(request):
    reservations = Reservation.objects.all()
    return render(request, 'reservation_list.html', {'reservations': reservations})

def schedule_reservation(request):
    logger.debug("Widok został wywołany")
    if request.method == "POST":
        logger.debug(f"Raw POST data: {request.POST}")
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            # Ustawienie end_time na podstawie czasu trwania usługi
            duration = reservation.service.duration
            reservation.end_time = reservation.start_time + duration
            
            # Sprawdenie, czy rezerwacja nie koliduje z inną
            conflicting_reservations = Reservation.objects.filter(
                hairdresser=reservation.hairdresser,
                start_time__lt=reservation.end_time,
                end_time__gt=reservation.start_time,
            )
            if conflicting_reservations.exists():
                messages.error(request, "Podany termin jest już zajęty, proszę wybrać inny termin.")
            else:
                reservation.save()
                messages.success(request, "Rezerwacja została pomyślnie zaplanowana.")
                return redirect('reservation_list')
        else:
            logger.debug(f"Form errors: {form.errors}")
            messages.error(request, "Wystąpił błąd w formularzu rezerwacji.")
    else:
        form = ReservationForm()

    return render(request, 'schedule_reservation.html', {'form': form})

def testowy(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reservation_list')  # Redirect to a new URL for success
    else:
        form = ReservationForm()

    return render(request, 'testowy.html', {'form': form})    