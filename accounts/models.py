from decimal import Decimal
from django.db import models
from management.models import Library, Member, VinylDistributor
from musicDatabase.models import VinylRelease
from vinylShop.models import StockItem


class OrderRequestItem(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='order_request_item_member')
    library = models.ForeignKey(Library, on_delete=models.PROTECT, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    #region to remove
    check_availability = models.BooleanField(default=False) # I think this can be deleted
    note = models.TextField(max_length=1000, blank=True, null=True) # this can probably go
    sent_to_invoice_receipt = models.BooleanField(default=False) # probably not needed and replaced with the below
    to_direct_shopping_invoice = models.BooleanField(default=False) # not sure if this is needed
    quantity_used_by_member = models.IntegerField(default=0) # probably redundant
    unavailable = models.BooleanField(default=False)
    date_when_set_to_unavailable = models.DateTimeField(blank=True, null=True)
    #endregion

    #region basic info
    vinyl_release = models.ForeignKey(VinylRelease, on_delete=models.PROTECT, related_name='order_request_items__vinyl_release+', null=True, blank=True)
    stock_item = models.ForeignKey(StockItem, on_delete=models.PROTECT, related_name='order_request_item_stock_item', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1) # need to make sure this can not be changed after order is placed, unless it is a shop stock item that will be used by a member
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    
    @property
    def sub_total(self):
        if self.sale_price != None:
            sub_t = self.quantity * self.sale_price
        else:
            sub_t = 0
        return sub_t
    
    @property
    def weight_item(self):
        release = VinylRelease.objects.get(catalog_number=self.vinyl_release)
        if release.plate_size == '7"':
            plate_weight = 3
        elif release.plate_size == '10"':
            plate_weight = 6
        else:
            plate_weight = 10
        item_weight = plate_weight * release.plate_count * self.quantity
        return item_weight
    
    #endregion
    #region purchase order request
    purchase_order_request_item = models.ForeignKey('PurchaseOrderRequestItem', on_delete=models.PROTECT, related_name='order_request_item_purchase_order_request_item', null=True, blank=True)
    #endregion
    #region status
    ordered = models.BooleanField(default=False)
    to_become_shop_stock = models.BooleanField(default=False)
    shop_purchase = models.BooleanField(default=False)
    stockpiled = models.BooleanField(default=False)
    invoiced = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    en_route = models.BooleanField(default=False) # might need to be added to courier package section
    delivered = models.BooleanField(default=False)
    hidden_from_member = models.BooleanField(default=False)
    #endregion

    def __str__(self):
        return str("{:05d}".format(self.pk))  + '_____'  + str(self.member.membership_number) + '_____' + str(self.vinyl_release)


class Invoice(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    library = models.ForeignKey(Library, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    member_has_made_payment = models.BooleanField(default=False)
    member_has_received_all_plates = models.BooleanField(default=False)
    member_archived = models.BooleanField(default=False)

    #region specifics
    invoice_weight = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    invoice_shipping_type = models.CharField(max_length=100, blank=True, null=True)
    invoice_shipping_cost = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    invoice_sub_total = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    invoice_gst = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    invoice_total_gst = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    invoice_discount_amount = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    invoice_total = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    
    @property
    def invoice_items(self):
        invoice_items = InvoiceItem.objects.filter(invoice=self)
        return invoice_items
    
    #endregion
                  
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.pk) + ' ' + str(self.member)


class InvoiceItem(models.Model):
    order_request_item = models.OneToOneField(OrderRequestItem, on_delete=models.PROTECT, related_name='order_request_items_invoice')   
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='invoice_items_invoice')
    invoiced_quantity = models.PositiveIntegerField(blank=True, null=True)
    invoiced_sale_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    invoiced_sub_total = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    invoiced_weight = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    
    def __str__(self):
        return str(self.order_request_item)


class PurchaseOrderRequest(models.Model):
    library = models.ForeignKey(Library, on_delete=models.PROTECT)
    distributor = models.ForeignKey(VinylDistributor, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def all_filled_or_unavailable(self):
        p_o_request_items = PurchaseOrderRequestItem.objects.filter(
            purchase_order_request=self)
        
        purchase_order_request_items = []
        for i in p_o_request_items:
            order_request_item = OrderRequestItem.objects.filter(purchase_order_request_item=i)
            for j in order_request_item:
                if j.unavailable != True and i.filled == True or j.unavailable == True:
                    purchase_order_request_items.append(i)
                    return True
                else:
                    return False
                    
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.library) + ' PO'  + str("{:04d}".format(self.pk))


class PurchaseOrderRequestItem(models.Model):
    purchase_order_request = models.ForeignKey(PurchaseOrderRequest, on_delete=models.PROTECT, related_name='purchase_order_request_item_purchase_order_request')
    vinyl_release = models.ForeignKey(VinylRelease, on_delete=models.PROTECT, related_name='order_request_items__vinyl_release+', null=True, blank=True)
    quantity_old = models.PositiveIntegerField(default=1)
    filled = models.BooleanField(default=False)

    @property
    def quantity(self):
        order_request_items = OrderRequestItem.objects.filter(purchase_order_request_item=self)
        q = 0
        for i in order_request_items:
            if i.purchase_order_request_item == self:
                q += i.quantity
        return q     

    def __str__(self):
        return ' PO'  + str("{:04d}".format(self.purchase_order_request.pk)) + ' ' + str(self.vinyl_release)  + '  x' + str(self.quantity)