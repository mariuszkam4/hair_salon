from django.db import models

class Hairdresser(models.Model):
    SPECIALIZATIONS = [
        ("M", 'Fryzjer męski'),
        ("D", "Fryzjer damski"),
        ("S", "Stylista"),
    ]
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=1, choices=SPECIALIZATIONS)

class Service(models.Model):
    name = models.CharField(max_length=100)
    duration = models.DurationField()
    cost = models.DecimalField(max_digits=5, decimal_places=2)

class Reservation(models.Model):
    hairdresser = models.ForeignKey(Hairdresser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date_time = models.DateField()