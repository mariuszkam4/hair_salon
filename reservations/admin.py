from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Hairdresser, Service, Reservation, SpecializationChoice


class HairdresserAdminForm(forms.ModelForm):
    specializations = forms.ModelMultipleChoiceField(
        queryset=SpecializationChoice.objects.all(),
        widget = FilteredSelectMultiple ('Specializations', is_stacked=False),
        required=False,
    )

    class Meta:
        model = Hairdresser
        fields = ('__all__')

    def __init__(self, *args, **kwargs):
        super(HairdresserAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['specializations'].initial = self.instance.specialization.all()
    
    def save(self, commit=True):
        instance = super(HairdresserAdminForm, self).save(commit=False)
        if commit:
            instance.save()
        if instance.pk:
            instance.specialization.set(self.cleaned_data['specializations'])
            self.save_m2m()
        return instance

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
        return ", ".join([s.specialization for s in obj.specialization.all()])
    list_specializations.short_description = 'Specializations'

admin.site.register(Hairdresser, HairdresserAdmin)
admin.site.register(Service)
admin.site.register(Reservation)
admin.site.register(SpecializationChoice)