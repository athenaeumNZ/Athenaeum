from django.contrib import admin
from accounts.models import (
    Invoice,
    InvoiceItem,
    OrderRequestItem,
    PurchaseOrderRequest,
    PurchaseOrderRequestItem,
)

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    search_fields = ['order_request_item__vinyl_release__catalog_number']


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'invoice_total', 'library', 'member_archived']
    search_fields = ['member__membership_number']
    inlines = [InvoiceItemInline]


class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_request_item', 'invoice',)
    search_fields = [
        'order_request_item__vinyl_release__catalog_number',
        'invoice__id',
        'order_request_item__member__membership_number',
    ]


class OrderRequestItemAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'vinyl_release', 'member', 'ordered', 'unavailable')
    list_filter = [
        'stockpiled',
        'to_become_shop_stock',
        'vinyl_release__distributor__distributor_code',
        'stock_item',
        'vinyl_release__distributor',
    ]
    search_fields = [
        'vinyl_release__catalog_number',
        'member__membership_number',
        'vinyl_release__distributor__distributor_code',
    ]


class PurchaseOrderRequestItemInline(admin.TabularInline):
    model = PurchaseOrderRequestItem
    extra = 0
    search_fields = ['vinyl_release__catalog_number']


class PurchaseOrderRequestAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'distributor', 'created']
    inlines = [PurchaseOrderRequestItemInline]


class PurchaseOrderRequestItemAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'vinyl_release', 'quantity', 'filled']
    search_fields = ['vinyl_release__catalog_number', 'id']


admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItem, InvoiceItemAdmin)
admin.site.register(OrderRequestItem, OrderRequestItemAdmin)
admin.site.register(PurchaseOrderRequest, PurchaseOrderRequestAdmin)
admin.site.register(PurchaseOrderRequestItem, PurchaseOrderRequestItemAdmin)
