from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as gl
from django.utils import timezone

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
    
    def has_specialization(self, specialization):
        return self.specialization.filter(specialization=specialization).exists()

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
    specializations = models.ManyToManyField(
        'SpecializationChoice',
        related_name='services',
        verbose_name='specializations',
    )

    def __str__(self):
        return self.name
    
    def get_specializations(self):
        return [spec.specialization for spec in self.specializations.all()]

class Reservation(models.Model):
    hairdresser = models.ForeignKey(Hairdresser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.hairdresser.name} rezerwacja na {self.start_time}"

    def clean(self):
        if self.start_time and not timezone.is_aware(self.start_time):
            start_datetime = timezone.make_aware(self.start_time)
        else:
            start_datetime = self.start_time

        if self.end_time is None:
            raise ValidationError(gl('Czas zakończenia musi być ustawiony.'))

        if not timezone.is_aware(self.end_time):
            raise ValidationError(gl('Czas zakończenia musi być wartością zgodną z obowiązującą strefą czasową.'))

        if self.end_time <= start_datetime:
            raise ValidationError(gl('Zakończenie rezerwacji nie może mieć miejsca przed terminem jej rozpoczęcia.'))

        service_specializations = self.service.get_specializations() if self.service else []
        if not any(self.hairdresser.has_specialization(spec) for spec in service_specializations):
            raise ValidationError(gl("Wybrany fryzjer nie ma specjalizacji do realizacji wskazanej usługi."))
 
    def save(self, *args, **kwargs):
        if not self.start_time:
            raise ValidationError("Czas rozpoczęcia musi być ustawiony.")
        
        if not self.service:
            raise ValidationError("Usługa musi być przypisana do rezerwacji.")

        if not isinstance(self.service.duration, timezone.timedelta):
            raise ValidationError("Czas trwania usługi musi być określony jako timedelta.")

        if not self.end_time:
            self.end_time = self.start_time + self.service.duration

        super().save(*args, **kwargs)