from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as gl
from django.utils import timezone
from datetime import datetime, time

class Hairdresser(models.Model):
    SPECIALIZATIONS = [
        ("M", "Fryzjer męski"),
        ("F", "Fryzjer damski"),
        ("S", "Stylista"),
    ]
    name = models.CharField(max_length=100)
    specialization = models.ManyToManyField(
        'SpecializationChoice',
        verbose_name='specializations',
        )

    def __str__(self):
        return self.name

class SpecializationChoice(models.Model):
    specialization = models.CharField(
        max_length=2,
        choices=Hairdresser.SPECIALIZATIONS,
        unique=True
    )

    def __str__(self):
        return self.get_specialization_display()
    
class Service(models.Model):
    name = models.CharField(max_length=100)
    duration = models.DurationField()
    cost = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    hairdresser = models.ForeignKey(Hairdresser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    start_time = models.DateField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.hairdresser.name} rezerwacja na {self.start_time}"
    
    def clean(self):
        # Konwersja start_time na datetime
        start_datetime = datetime.combine(self.start_time, time.min)
        start_datetime = timezone.make_aware(start_datetime)
        
        # Sprawdzenie, czy end_time jest instancją datetime
        if not isinstance(self.end_time, datetime):
            raise ValidationError(gl('Czas zakończenia musi być dokładną datą i czasem.'))
        
        if self.end_time <= start_datetime:
            raise ValidationError(gl('Zakończenie rezerwacji nie może mieć miejsca przed terminem jej rozpoczęcia.'))
    
    def save(self, *args, **kwargs):
        if self.service and self.service.duration and not self.end_time:
            start_datetime = datetime.combine(self.start_time, time.min)
            start_datetime = timezone.make_aware(start_datetime)
            self.end_time = start_datetime + self.service.duration 
        super().save(*args, **kwargs)