from django.test import TestCase
from .forms import ReservationForm, ServiceAdminForm
from .models import Hairdresser, Service, SpecializationChoice, Reservation
from datetime import timedelta, date, time

class ReservationFormTests(TestCase):

    def setUp(self):
        self.specialization = SpecializationChoice.objects.create(specialization="M")
        self.hairdresser = Hairdresser.objects.create(name="Testowy Fryzjer")
        self.hairdresser.specialization.add(self.specialization)
        self.service = Service.objects.create(
            name="Strzyżenie", 
            duration = timedelta(hours=1), 
            cost=100
        )        
        self.service.specializations.add(self.specialization)
    
    def test_valid_data(self):
        form = ReservationForm(data={
            'hairdresser': self.hairdresser.id,
            'service': self.service.id,
            'start_date': '2023-01-01',
            "start_time": "10:00",
            'end_time': '11:00'
        })
        print (form.errors)
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = ReservationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('hairdresser', form.errors)
        self.assertIn('service', form.errors)
        self.assertIn('start_date', form.errors)
        self.assertIn('start_time', form.errors)
    
    def test_clean_with_end_time_earlier_than_start_time(self):
        # Przypadek z ustawionym czasem end_time przed czasem start_time
        form = ReservationForm(data={
            'hairdresser': self.hairdresser.id,
            'service': self.service.id,
            'start_date': '2023-01-01',
            'start_time': '10:00',
            'end_time': '09:00'
        })
        self.assertFalse(form.is_valid())
        
    def test_clean_with_auto_setting_end_time(self):
        # Sprawdzenie czy czas end_time jest automatycznie ustawiany
        form = ReservationForm(data={
            'hairdresser': self.hairdresser.id,
            'service': self.service.id,
            'start_date': '2023-01-01',
            'start_time': '09:00'
        })
        print (form.errors)
        self.assertTrue(form.is_valid())
        self.assertIsNotNone(form.cleaned_data['end_time'])

    def test_save_new_reservation(self):
        # Sprawdzenie czy metoda save poprawnie tworzy nową instancję modelu Reservation
        form = ReservationForm(data={
            'hairdresser': self.hairdresser.id,
            'service': self.service.id,
            'start_date': '2023-01-01',
            'start_time': '10:00',
            'end_time': "11:00"
        })
        if form.is_valid():
            reservation = form.save()
            self.assertIsNotNone(reservation.pk)
            self.assertEqual(reservation.hairdresser, self.hairdresser)
            self.assertEqual(reservation.service, self.service)
        else:
            self.fail("Formularz powinien być poprawny")
    
    def test_update_existing_reservation(self):
        reservation = Reservation.objects.create(
            hairdresser = self.hairdresser,
            service = self.service,
            start_date=date(2023, 1, 1),
            start_time=time(10, 0),
            end_time=time(11, 0)
        )

        form = ReservationForm(instance=reservation, data={
            'hairdresser': self.hairdresser.id,
            'service': self.service.id,
            'start_date': '2023-01-02',
            'start_time': '11:00',
            'end_time': "12:00"
        })
        if form.is_valid():
            updated_reservation = form.save()
            self.assertEqual(updated_reservation.start_date, date(2023, 1, 2))
            self.assertEqual(updated_reservation.start_time, time(11, 0))
            self.assertEqual(updated_reservation.end_time, time(12, 0))
        else:
            self.fail("Formularz powinien być poprawny")
    
    def test_save_with_auto_end_time(self):
        form = ReservationForm(data={
            'hairdresser': self.hairdresser.id,
            'service': self.service.id,
            'start_date': '2023-01-02',
            'start_time': '11:00',
        })
        if form.is_valid():
            reservation = form.save()
            self.assertIsNotNone(reservation.end_time)
        else:
            self.fail("Formularz powinien być poprawny")

class ServiceAdminFormTests(TestCase):
    # Sprawdenie czy formluarz poprawnie tworzy nową usługę
    def setUp(self):
        self.spec1 = SpecializationChoice.objects.create(specialization="M")
        self.spec2 = SpecializationChoice.objects.create(specialization="F")

    def test_valid_data(self):
        form = ServiceAdminForm(data={
            'name': "Test Service",
            'duration': timedelta(hours=1),
            'cost': 100,
            'specializations': [self.spec1.pk, self.spec2.pk]
        })
        self.assertTrue(form.is_valid())

    def test_create_new_service(self):
        form = ServiceAdminForm(data={
            'name': "New Service",
            'duration': timedelta(hours=2),
            'cost': 200,
            'specializations': [self.spec1.pk]
        })
        if form.is_valid():
            service = form.save()
            self.assertIsNotNone(service.pk)
            self.assertEqual(service.name, "New Service")
            self.assertIn(self.spec1, service.specializations.all())
        else:
            self.fail("Formularz powinien być poprawny.")

    def test_update_existing_service(self):
        service = Service.objects.create(
            name = "Usługa istniejąca",
            duration = timedelta (hours=1),
            cost = 100,
        )
        service.specializations.add(self.spec1)
        self.assertTrue(SpecializationChoice.objects.filter(pk=self.spec2.pk).exists())

        form = ServiceAdminForm(instance=service, data={
            'name': 'Usługa zaktualizowana',
            'duration': timedelta(hours=2),
            'cost': 200,
            'specializations': [self.spec2.pk]
        })
        if form.is_valid():
            updated_service = form.save()
            self.assertEqual(updated_service.name, "Usługa zaktualizowana")
            self.assertEqual(updated_service.duration, timedelta(hours=2))
            self.assertEqual(updated_service.cost, 200)
            self.assertIn(self.spec2, updated_service.specializations.all())
            self.assertNotIn(self.spec1, updated_service.specializations.all())
        else:
            self.fail("Formularz powinien być poprawny")

    def test_missing_required_fields(self):
        form = ServiceAdminForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('duration', form.errors)
        self.assertIn('cost', form.errors)

