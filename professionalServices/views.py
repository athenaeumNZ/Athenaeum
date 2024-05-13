from django.shortcuts import render

from professionalServices.models import ProfessionalServicesInvoice, ProfessionalServicesInvoiceHour
from management.models import Library

def portfolio(request):
    context = {
    }
    return render(request, 'portfolio.html', context)

#region professional services

def professional_services_invoice(request, library_id, invoice_id):
    library = Library.objects.get(id=library_id)
    invoice = ProfessionalServicesInvoice.objects.get(id=invoice_id)
    invoice_hours = ProfessionalServicesInvoiceHour.objects.filter(invoice=invoice)
    ## bank_account = BankAccount.objects.get(account_holder=invoice.service_provider)
    context = {
        'library': library,
        'invoice': invoice,
        'invoice_hours': invoice_hours,
    }
    return render(request,'professional_services_invoice.html', context)

def professional_services_invoice_paid_submission(request, library_id, invoice_id):
    library = Library.objects.get(id=library_id)
    invoice = ProfessionalServicesInvoice.objects.get(id=invoice_id)
    invoice.paid = True
    invoice.save()
    context = {
        'library': library,
        'invoice': invoice,
    }
    return render(request,'return_to_professional_services_invoice.html', context)

def return_to_professional_services_invoice(request, library_id, invoice_id, service_provider_id):
    library = Library.objects.get(id=library_id)
    invoice = ProfessionalServicesInvoice.objects.get(id=invoice_id,service_provider=service_provider_id)
    context = {
        'library': library,
        'invoice': invoice,
    }
    return render(request,'return_to_professional_services_invoice.html', context)

#endregion
