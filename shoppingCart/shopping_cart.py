from decimal import Decimal

from django.conf import settings

from vinylShop.models import StockItem

class ShoppingCart(object):
    #region start shopping cart session or if already started, use that session
    def __init__(self, request):
        self.session = request.session
        shopping_cart = self.session.get(settings.SHOPPING_CART_SESSION_ID)
        if not shopping_cart:
            shopping_cart = self.session[settings.SHOPPING_CART_SESSION_ID] = {}
        self.shopping_cart = shopping_cart
    #endregion
    #region add stock item to cart
    def add(self, stock_item): # removed -> , quantity=1, update_quantity=False
        stock_item_id = str(stock_item.id)
        if stock_item_id not in self.shopping_cart:
            if stock_item.price != 999.00:
                price = str(stock_item.price)
            else:
                price = 0
            self.shopping_cart[stock_item_id] = {
                'price': str(price),
                }
        self.save()
    #endregion
    #region save cart
    def save(self):
        self.session[settings.SHOPPING_CART_SESSION_ID] = self.shopping_cart
        self.session.modified = True
    #endregion
    #region remove item from cart
    def remove(self, stock_item):
        stock_item_id = str(stock_item.id)
        if stock_item_id in self.shopping_cart:
            del self.shopping_cart[stock_item_id]
            self.save()
    #endregion
    #region iterate through items
    def __iter__(self):
        stock_item_ids = self.shopping_cart.keys()
        stock_items = StockItem.objects.filter(id__in=stock_item_ids)
        for item in stock_items:
            self.shopping_cart[str(item.pk)]['item'] = item # changed id to pk, seems to work fine

        for item in self.shopping_cart.values():
            item['price'] = Decimal(item['price'])
            yield item
    #endregion
    #region create the items_list
    def items_list(self):
        stock_item_ids = self.shopping_cart.keys()
        stock_items = StockItem.objects.filter(id__in=stock_item_ids).order_by('vinyl_release__catalog_number')
        return stock_items
    #endregion
    #region calculate total
    def get_total_price(self):
        return sum(Decimal(item['price']) for item in self.shopping_cart.values())
    #endregion  
    #region calculate total
    def some_items_price_not_set(self):
        items_l = self.items_list()
        set = True
        for i in items_l:
            if i.price == 999.00:
                set = False
        return set
    
    #endregion  
    #region clear shopping cart
    def clear(self):
        del self.session[settings.SHOPPING_CART_SESSION_ID]
        self.session.modified = True
    #endregion
    ''' OLD 
    # not sure if this is needed or why it is price this looks to be from when the price needed to be the total or a sum of the quantities
    def get_items_list(self):
        return sum(Decimal(item['price']) for item in self.shopping_cart.values())
    '''
    