from django.contrib import admin
from django.db import models
from django.forms import Textarea
from professionalServices.models import Client, ProfessionalServiceType, ProfessionalServicesInvoice, ProfessionalServicesInvoiceHour

admin.site.register(Client)
admin.site.register(ProfessionalServiceType)
class ProfessionalServicesInvoiceHourInline(admin.TabularInline):
    model = ProfessionalServicesInvoiceHour
    fields = ['service_type', 'quantity', 'fee', 'notes',]
    readonly_fields = ('fee',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    }
    extra = 0

admin.site.register(ProfessionalServicesInvoiceHour)

class ProfessionalServicesInvoiceAdmin(admin.ModelAdmin):
    inlines = [ProfessionalServicesInvoiceHourInline]

    
admin.site.register(ProfessionalServicesInvoice, ProfessionalServicesInvoiceAdmin)
