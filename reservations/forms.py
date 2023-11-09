from django import forms
from .models import Reservation, Service
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Service, SpecializationChoice, Hairdresser, Reservation
import logging

logger = logging.getLogger(__name__)

class ReservationForm(forms.ModelForm):
    end_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(
        attrs={'type': 'datetime-local'},
        format = '%Y-%m-%dT%H:%M'),
        input_formats=('%Y-%m-%dT%H:%M',)
        )
    
    class Meta:
        model = Reservation
        fields = ['hairdresser', 'service', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        service = cleaned_data.get("service")
        end_time = cleaned_data.get("end_time")

        logger.debug(f"Cleaned start time: {start_time}")
        logger.debug(f"Cleaned service: {service}")
        logger.debug(f"Cleaned end time: {end_time}")       

        if service and start_time and not end_time:
            # Oblicz czas zakończenia na podstawie czasu trwania usługi
            cleaned_data['end_time'] = start_time + service.duration
            end_time = cleaned_data['end_time']
            
            if end_time <= start_time:
                raise ValidationError(_('Czas zakończenia usługi musi być później niż czas jej rozpoczęcia.'))

        return cleaned_data

    def save(self, commit=True):
        instance = super(ReservationForm, self).save(commit=False)
        if not instance.end_time and instance.service and instance.start_time:
            # Ustaw czas zakończenia na podstawie czasu trwania usługi
            instance.end_time = instance.start_time + instance.service.duration
        if commit:
            instance.save()
        return instance

class ServiceAdminForm(forms.ModelForm):
    specializations = forms.ModelMultipleChoiceField(
        queryset=SpecializationChoice.objects.all(),
        widget=FilteredSelectMultiple('Specializations', is_stacked=False),
        required=False,
    )

    class Meta:
        model = Service
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['specializations'].initial = self.instance.specializations.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        if instance.pk:
            instance.specializations.set(self.cleaned_data['specializations'])
            self.save_m2m()
        return instance

class HairdresserAdminForm(forms.ModelForm):
    specializations = forms.ModelMultipleChoiceField(
        queryset=SpecializationChoice.objects.all(),
        widget=FilteredSelectMultiple('Specializations', is_stacked=False),
        required=False,
    )

    class Meta:
        model = Hairdresser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(HairdresserAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['specialization'].initial = self.instance.specialization.all()
    
    def save(self, commit=True):
        hairdresser = super(HairdresserAdminForm, self).save(commit=False)
        if commit:
            hairdresser.save()
        if hairdresser.pk:
            hairdresser.specialization.set(self.cleaned_data['specialization'])
            self.save_m2m()
        return hairdresser