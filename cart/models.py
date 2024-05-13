from django.db import models

from management.models import Library
from musicDatabase.models import VinylRelease
from vinylLibrary.models import Member, LibraryPlate

class Order(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    library = models.ForeignKey(Library, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    on_order = models.BooleanField(default=False)
    mark_up_removed = models.BooleanField(default=False)
    credit_used = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default= 0.00)
    cashbook_entry_added = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.member) + ' ' + str(self.created) + ' ' + str(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all()) - self.credit_used
    
    def get_gst(self):
        return (sum(item.get_cost() for item in self.items.all()) - self.credit_used) / 115 * 15

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    vinyl_release = models.ForeignKey(VinylRelease, on_delete=models.PROTECT, related_name='order_items', null=True, blank=True)
    library_plate = models.ForeignKey(LibraryPlate, on_delete=models.SET_NULL, related_name='order_items_lp', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    recieved = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)
    ordered = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)

    def get_cost(self):
        total = self.price * self.quantity
        return total

class PurchaseOrder(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    library = models.ForeignKey(Library, on_delete=models.PROTECT)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    funded = models.BooleanField(default=False)
    on_order = models.BooleanField(default=False)
    cashbook_entry_added = models.BooleanField(default=False)

    is_restock = models.BooleanField(default=False)
    
    def order_total(self):
        items = PurchaseOrderItem.objects.filter(purchase_order=self)
        total = 0
        for i in items:
            total += i.total_price()
        return total
    
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.member) + ' ' + str(self.created) + ' ' + str(self.id)

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='purchase_items')
    vinyl_release = models.ForeignKey(VinylRelease, on_delete=models.PROTECT, related_name='purchase_order_items', null=True, blank=True)
    library_plate = models.ForeignKey(LibraryPlate, on_delete=models.SET_NULL, related_name='purchase_order_items_lp', null=True, blank=True)
    ordered = models.BooleanField(default=False)
    recieved = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        total = self.price * self.quantity
        return total

    def __str__(self):
        return str(self.id)
