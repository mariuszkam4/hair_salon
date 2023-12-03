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
    class Meta:
        model = Reservation
        fields = ['hairdresser', 'service', 'start_date', 'start_time', 'end_time']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'required': False}),
        }

    def clean(self):        
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        service = cleaned_data.get('service')
        hairdresser = cleaned_data.get('hairdresser')

        errors = {}
        if not hairdresser:
            errors['hairdresser'] = ValidationError(_('Należy wskazać fryzjera do wykonania usługi'))
        if not start_date:
            errors['start_date'] = ValidationError(_('Data rozpoczęcia rezerwacji jest wymagana.'))
        if not start_time:
            errors['start_time'] = ValidationError(_('Czas rozpoczęcia rezerwacji jest wymagany.'))
        if not service:
            errors['service'] = ValidationError(_('Podanie usługi jest wymagane w rezerwacji.'))
        
        if errors:
            raise ValidationError(errors)

        start_datetime = timezone.make_aware(datetime.combine(start_date, start_time))

        if end_time:
            end_datetime = timezone.make_aware(datetime.combine(start_date, end_time))
            if end_datetime < start_datetime:
                raise ValidationError(_('Czas zakończenia nie może być wcześniejszy niż czas rozpoczęcia.'))
        else:
            # Obliczenie domyślnego czasu zakończenia na podstawie czasu trwania usługi"                        
            end_datetime = start_datetime + service.duration
            cleaned_data['end_time'] = end_datetime.time()

        return cleaned_data

    def save(self, commit=True):
        instance = super(ReservationForm, self).save(commit=False)
        if instance.start_date and instance.start_time and instance.service:
            start_datetime = timezone.make_aware(datetime.combine(instance.start_date, instance.start_time))
            
            # Użyj end_time z cleaned_data
            end_time = self.cleaned_data.get('end_time')
            if end_time:
                instance.end_time = end_time                
            else:
                # Ustawienie czasu zakończenia tylko, gdy nie został podany ręcznie
                instance.end_time = (start_datetime + instance.service.duration).time()                

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
            self.fields['specializations'].initial = self.instance.specialization.all()
    
    def save(self, commit=True):
        hairdresser = super(HairdresserAdminForm, self).save(commit=False)
        if commit:
            hairdresser.save()
        if hairdresser.pk:
            hairdresser.specialization.set(self.cleaned_data['specializations'])
            self.save_m2m()
        return hairdresser