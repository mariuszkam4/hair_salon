from django.shortcuts import render
from django.contrib import messages
from .models import Hairdresser, Service, Reservation
from .forms import ReservationForm

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
    if request.method == "POST":
        form = ReservationForm(request.POST)
        if form.is_valid():
            selected_hairdresser = form.cleaned_data['hairdresser']
            selected_date = form.cleaned_data['date']
            selected_time = form.cleaned_data['time']

            existing_reservation = Reservation.objects.filter(
                hairdresser=selected_hairdresser, 
                date=selected_date, 
                time=selected_time,
                )
            if existing_reservation.exists():
                messages.error(request, "Podany termin jest już zajęty, proszę wybrać inny termin.")
            
        else:
            form = ReservationForm()
        
        return render(request, 'schedule_reservation.html', {'form': form})