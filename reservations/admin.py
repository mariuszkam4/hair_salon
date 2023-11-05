from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Hairdresser, Service, Reservation, SpecializationChoice

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
            self.fields['specializations'].initial = self.instance.specializations.all()
    
    def save(self, commit=True):
        hairdresser = super(HairdresserAdminForm, self).save(commit=False)
        if commit:
            hairdresser.save()
        if hairdresser.pk:
            hairdresser.specializations.set(self.cleaned_data['specializations'])
            self.save_m2m()
        return hairdresser

class HairdresserAdmin(admin.ModelAdmin):
    form = HairdresserAdminForm
    list_display = ['name', 'list_specializations']
    search_fields = ['name']

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css',),
        }
        js = ('/admin/jsi18n',)

    def list_specializations(self, obj):
        return ", ".join([s.get_specialization_display() for s in obj.specializations.all()])
    list_specializations.short_description = 'Specializations'

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'duration', 'list_specializations')

    def list_specializations(self, obj):
        return ", ".join([spec.get_specialization_display() for spec in obj.specializations.all()])
    list_specializations.short_description = 'Specializations'

admin.site.register(Hairdresser, HairdresserAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Reservation)
admin.site.register(SpecializationChoice)
