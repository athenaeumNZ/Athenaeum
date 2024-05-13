from decimal import Decimal

from django.conf import settings

from musicDatabase.models import VinylRelease

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, vinyl_release, quantity=1, update_quantity=False):
        vinyl_release_id = str(vinyl_release.id)
        if vinyl_release_id not in self.cart:
            self.cart[vinyl_release_id] = {
                'pre_sale_sale_price': str(vinyl_release.pre_sale_price_NZ),
                }
        self.save()


    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, vinyl_release):
        vinyl_release_id = str(vinyl_release.id)
        if vinyl_release_id in self.cart:
            del self.cart[vinyl_release_id]
            self.save()

    def __iter__(self):
        vinyl_release_ids = self.cart.keys()
        library_sale_vinyls = VinylRelease.objects.filter(id__in=vinyl_release_ids)
        for vinyl_release in library_sale_vinyls:
            self.cart[str(vinyl_release.id)]['vinyl_release'] = vinyl_release

        for item in self.cart.values():
            item['price'] = Decimal(item['pre_sale_sale_price'])
            yield item
    
    '''used?'''
    def items_list(self):
        vinyl_release_ids = self.cart.keys()
        library_sale_vinyls = VinylRelease.objects.filter(id__in=vinyl_release_ids)
        return library_sale_vinyls
    ''''''

    def get_total_price(self):
        return sum(Decimal(item['pre_sale_sale_price']) for item in self.cart.values())
    
    '''used?'''
    def get_items_list(self):
        return sum(Decimal(item['pre_sale_sale_price']) for item in self.cart.values())
    ''''''
    
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
