from django.contrib import admin

from cart.models import Order, OrderItem, PurchaseOrder, PurchaseOrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['library_plate']
    search_fields = ['vinyl_release__catalog_number']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'library', 'paid',
                    'on_order', 'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    search_fields = ['member__membership_number']
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('vinyl_release', 'id', 'recieved')
    search_fields = ['vinyl_release__catalog_number']

admin.site.register(OrderItem, OrderItemAdmin)




class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    raw_id_fields = ['library_plate']

class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'library', 
                    'on_order', 'created', 'updated']
    list_filter = ['created', 'updated']
    inlines = [PurchaseOrderItemInline]

admin.site.register(PurchaseOrder, PurchaseOrderAdmin)

class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('vinyl_release', 'id', 'recieved')
    search_fields = ['vinyl_release__catalog_number']

admin.site.register(PurchaseOrderItem, PurchaseOrderItemAdmin)