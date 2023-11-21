from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime

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
    start_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)    

    def __str__(self):
        return f"{self.hairdresser.name} rezerwacja na {self.start_date} o godz. {self.start_time}"

    def clean(self):
        if self.hairdresser_id and self.start_date and self.start_time and self.service:
            start_datetime = timezone.make_aware(datetime.combine(self.start_date, self.start_time))
            end_datetime = start_datetime + self.service.duration

            if end_datetime.date() != self.start_date:
                raise ValidationError(_('Rezerwacja musi zakończyć się tego samego dnia.'))

            self.end_time = end_datetime.time()
        else:
            raise ValidationError(_('Wypełnij wszystkie wymagane pola.'))
        
        service_specializations = self.service.get_specializations() if self.service else []
        if not any(self.hairdresser.has_specialization(spec) for spec in service_specializations):
            raise ValidationError(_("Wybrany fryzjer nie ma specjalizacji do realizacji wskazanej usługi"))

    def save(self, *args, **kwargs):
        if not (self.hairdresser and self.start_date and self.start_time and self.service):
            raise ValidationError(_('Fryzjer, data i godzina rozpoczęcia oraz usługa są wymagane.'))

        start_datetime = timezone.make_aware(datetime.combine(self.start_date, self.start_time))

        if not self.end_time:
            end_datetime = start_datetime + self.service.duration
            self.end_time = end_datetime.time()

        if self.end_time:
            end_datetime = timezone.make_aware(datetime.combine(self.start_date, self.end_time))
            if end_datetime < start_datetime:
                raise ValidationError(_('Czas zakończenia nie może być wcześniejszy niż czas rozpoczęcia.'))

        super().save(*args, **kwargs)