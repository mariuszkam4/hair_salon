from django.test import TestCase
from django.utils import timezone
from .models import Hairdresser, SpecializationChoice, Service, Reservation
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib.admin.sites import AdminSite
from .admin import ReservationAdmin
from .forms import ReservationForm
from datetime import datetime

class HairdresserSpecializationTestCase(TestCase):
    def setUp(self):
        # Tworzenie specjalizacji
        SpecializationChoice.objects.create(specialization='M')
        SpecializationChoice.objects.create(specialization='F')
        SpecializationChoice.objects.create(specialization='S')
        
        # Tworzenie fryzjerów
        self.hairdresser1 = Hairdresser.objects.create(name='Fryzjer1')
        self.hairdresser2 = Hairdresser.objects.create(name='Fryzjer2')
        self.hairdresser3 = Hairdresser.objects.create(name='Fryzjer3')

        # Przypisywanie specjalizacji
        self.hairdresser1.specialization.add(
            SpecializationChoice.objects.get(specialization='M')
        )
        self.hairdresser2.specialization.add(
            SpecializationChoice.objects.get(specialization='F')
        )
        # Fryzjer 3 ma dwie specjalizacje
        self.hairdresser3.specialization.add(
            SpecializationChoice.objects.get(specialization='F'),
            SpecializationChoice.objects.get(specialization='S')
        )

    def test_specialization_assignment(self):
        # Testowanie przypisania specjalizacji dla fryzjera 1
        self.assertEqual(self.hairdresser1.specialization.count(), 1)
        self.assertTrue(self.hairdresser1.specialization.filter(specialization='M').exists())

        # Testowanie przypisania specjalizacji dla fryzjera 2
        self.assertEqual(self.hairdresser2.specialization.count(), 1)
        self.assertTrue(self.hairdresser2.specialization.filter(specialization='F').exists())

        # Testowanie przypisania specjalizacji dla fryzjera 3
        self.assertEqual(self.hairdresser3.specialization.count(), 2)
        self.assertTrue(self.hairdresser3.specialization.filter(specialization='F').exists())
        self.assertTrue(self.hairdresser3.specialization.filter(specialization='S').exists())

class ReservationModelTests(TestCase):

    def setUp(self):
        # Tworzenie instancji fryzjera
        self.hairdresser = Hairdresser.objects.create(name="Testowy fryzjer")

        # Specjalizacja 
        SpecializationChoice.objects.create(specialization = "M")        
        
        # Tworzenie instancji usługi
        self.duration = timedelta(hours=1) 

        self.service = Service.objects.create(
            name="Test service", 
            duration=self.duration, 
            cost = 100, 
        )
        self.service.specializations.add(
            SpecializationChoice.objects.get(specialization='M'),            
        )

        # Czas początku rezerwacji do użycia w testach
        self.start_time = timezone.now().replace(second=0, microsecond=0)
   
    def test_reservation_end_time_auto_set(self):
        # Utworzenie rezerwacji bez jawnie ustwionego 'end_time'
        reservation = Reservation(
            hairdresser = self.hairdresser,
            service = self.service,
            start_date = self.start_time.date(),
            start_time = self.start_time.time(),
        )
        reservation.save()
        # Sprawdzenie czy end_time' został ustawiony automatycznie
        self.assertEqual(reservation.end_time, (self.start_time + self.duration).time())
    
    def test_reservation_end_time_manual_set(self):
        # Utworzenie rezerwacji z jawnie ustawionym 'end_time'
        end_time = (self.start_time + timedelta(hours=2)).time()
        reservation = Reservation(
            hairdresser = self.hairdresser,
            service = self.service,
            start_date = self.start_time.date(),
            start_time = self.start_time.time(),
            end_time = end_time,
        )
        reservation.save()
        # Sprawdzenie, czy 'end_time' odpowiada ręcznie ustawionej wartości
        self.assertEqual(reservation.end_time, end_time)      
        
    # Test specjalizacji fryzjera
    def test_reservation_with_invalid_hairdresser_raises_error(self):
        # Ustalamy, że fryzjer nie ma wymaganej specjalizacji
        self.hairdresser.specialization.clear()         
        with self.assertRaises(ValidationError):
            reservation = Reservation(
                hairdresser=self.hairdresser,
                service=self.service,
                start_time=self.start_time
            )
            reservation.full_clean()  # Walidacja powinna zawieść

