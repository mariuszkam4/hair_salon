from django.test import TestCase
from .forms import ReservationForm
from .models import Hairdresser, Service, SpecializationChoice
from datetime import timedelta

class ReservationFormTests(TestCase):

    def setUp(self):
        self.hairdresser = Hairdresser.objects.create(name="Testowy Fryzjer")
        self.service = Service.objects.create(
            name="Strzyżenie", 
            duration = timedelta(hours=1), 
            cost=100
        )
    
    def test_valid_data(self):
        form = ReservationForm(data={
            'hairdresser': self.hairdresser.id,
            'service': self.service.id,
            'start_date': '2023-01-01',
            "start_time": "10:00",
            'end_time': '11:00'
        })
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
            'start_time': '09:00'
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
        self.assertTrue(form.is_valid())
        self.assertIsNotNone(form.cleaned_data['end_time'])

    