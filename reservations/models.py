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
    end_time = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.hairdresser.name} rezerwacja na {self.start_time}"

    def clean(self):
        print ("Metoda clean w modelu wywołana")
        print (f"Czas start_time wygląda tak: {self.start_time}")
        if not self.start_time:
            raise ValidationError("Czas rozpoczęcia musi być ustawiony.")      
        elif not timezone.is_aware(self.start_time):
            self.start_time = timezone.make_aware(self.start_time)
        
        if not self.end_time and self.service:
            # Ustawienie end_time jako świadoma strefa czasowa
            naive_end_time = self.start_time + self.service.duration
            self.end_time = timezone.make_aware(naive_end_time, timezone.get_default_timezone())

        try:
            if self.end_time and not timezone.is_aware(self.end_time):
                raise ValidationError(gl('Czas zakończenia musi być wartością zgodną z obowiązującą strefą czasową.'))

            if self.end_time and self.end_time <= self.start_time:
                raise ValidationError(gl('Zakończenie rezerwacji nie może mieć miejsca przed terminem jej rozpoczęcia.'))
        except ValidationError as e:
            print (f"Błędy walidacji metody clean w modelu:\n{e}")
            raise e
        
    def save(self, *args, **kwargs):
        if not self.service:
            raise ValidationError("Usługa musi być przypisana do rezerwacji.")

        if not isinstance(self.service.duration, timezone.timedelta):
            raise ValidationError("Czas trwania usługi musi być określony jako timedelta.")

        # Upewniamy się, że start_time jest świadomy strefy czasowej
        if self.start_time and not timezone.is_aware(self.start_time):
            self.start_time = timezone.make_aware(self.start_time, timezone.get_default_timezone())

        # Ustawiamy end_time jako świadomy strefy czasowej
        if not self.end_time:
            naive_end_time = self.start_time + self.service.duration
            self.end_time = timezone.make_aware(naive_end_time, timezone.get_default_timezone())

        try:
            self.clean()
        except ValidationError as e:
            print (f"Błędy walidacji metody save modelu:\n{e}")
            raise e
        
        super().save(*args, **kwargs)