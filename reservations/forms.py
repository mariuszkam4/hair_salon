from django import forms
from .models import Hairdresser, Service

class ReservationsForm(forms.Form):
    hairdresser = forms.ModelChoiceField(queryset=Hairdresser.objects.all())
    service = forms.ModelChoiceField(queryset=Service.objects.all())
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.DateInput(attrs={'type': 'time'}))
