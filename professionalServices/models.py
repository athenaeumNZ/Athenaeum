from decimal import Decimal
from django.db import models

from management.models import Address, Member

class Client(models.Model):
    name = models.CharField(max_length=100, null=True)
    address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True, related_name='address_client')
    def __str__(self):
        return str(self.name)

class ProfessionalServiceProviderService(models.Model):
    service_provider = models.ForeignKey(Member, on_delete=models.PROTECT, null=True, related_name='professional_service_provider_service_service_provider')
    professional_service_type = models.ForeignKey('ProfessionalServiceType', on_delete=models.PROTECT, null=True, related_name='professional_service_provider_service_professional_service_type')
    description = models.CharField(max_length=100, null=True, blank=True)
    fee_nzd = models.PositiveIntegerField()

    class Meta:
        ordering = ('professional_service_type',)

    def __str__(self):
        return str(self.professional_service_type)
    
class ProfessionalServicesInvoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='professional_service_invoice_client')
    service_provider = models.ForeignKey(Member, on_delete=models.PROTECT, limit_choices_to={'is_professional_service_provider':True}, null=True, related_name='professional_service_invoice_service_provider')
    created = models.DateTimeField(blank=True, null=True, editable=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    notes = models.TextField(max_length=2000, null=True, blank=True)

    @property
    def invoice_sub_total(self):
        invoice_hours = ProfessionalServicesInvoiceHour.objects.filter(invoice=self)
        total = Decimal('0')
        for i in invoice_hours:
            total += Decimal(i.total_fee)
        return total
     
    @property
    def invoice_gst(self):
        gst = self.invoice_sub_total / 100 * 15
        return round(gst,2)

    @property
    def invoice_total(self):
        total = self.invoice_sub_total + self.invoice_gst
        return round(total,2)

    class Meta:
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(fields=['id', 'service_provider'], name='unique_id_service_provider_id')
        ]

    def __str__(self):
        return str(self.service_provider)
    
class ProfessionalServiceType(models.Model):
    name = models.CharField(max_length=100, null=True)
    notes = models.TextField(max_length=2000, null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return str(self.name)
    
class ProfessionalServicesInvoiceHour(models.Model):
    invoice = models.ForeignKey(ProfessionalServicesInvoice, on_delete=models.PROTECT, related_name='invoice_hour_invoice')
    service_type = models.ForeignKey(ProfessionalServiceProviderService, on_delete=models.CASCADE, limit_choices_to={'service_provider':10},  blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(max_length=1000, default='', blank=True, null=True)
    @property
    def hourly_fee(self):
        if self.service_type != None:
            return self.service_type.fee_nzd
        else:
            return 0
    
    @property
    def fee(self):
        return '$' + str(self.hourly_fee)

    @property
    def total_fee(self):
        total = Decimal(self.hourly_fee) * Decimal(self.quantity)
        return round(total, 2)
    
    def __str__(self):
        return str(self.service_type)
