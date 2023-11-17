from django import forms
from .models import Reservation, Service
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.utils import timezone
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
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']
 
    def clean(self):
        print("Metoda clean w ReservationForm wywołana")
        print(f"Widget output: {self['start_time'].value()}")
        print (f"Surowe dane POST : {self.data}")
        cleaned_data = super().clean()
        print(f"Cleaned data: {cleaned_data}")
        print(f"Błędy walidacji: {self.errors}")
        
        raw_start_time = self.data.get("start_time")
        print(f"Raw start time from POST data: {raw_start_time}")
        
        if raw_start_time:
            try:
                naive_start_time = datetime.strptime(raw_start_time, "%Y-%m-%dT%H:%M")
                aware_start_time = timezone.make_aware(naive_start_time, timezone.get_default_timezone())
                cleaned_data["start_time"] = aware_start_time
            except ValueError:
                self.add_error('start_time', "Nieprawidłowy format daty i godziny.")
                return cleaned_data  
                         
        start_time = cleaned_data.get("start_time")
        service = cleaned_data.get("service")
        end_time = cleaned_data.get("end_time")
       
        print (f"Start_time po walidacji metodą clean w ReservationForm:{start_time}")
        print (f"Format daty po metodzie clean w formularzu: {type(start_time)}")
        print (f"Cleaned service: {service}")
        print (f"Cleaned end time: {end_time}")       

        if service and start_time and not end_time:
            # Oblicz czas zakończenia na podstawie czasu trwania usługi
            cleaned_data['end_time'] = start_time + service.duration
            end_time = cleaned_data['end_time']
            
            if end_time <= start_time:
                raise ValidationError(_('Czas zakończenia usługi musi być później niż czas jej rozpoczęcia.'))

        print (f"Błędy w ReservationForm {self.errors}")
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