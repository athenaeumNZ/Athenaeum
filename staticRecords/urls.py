from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('vinylLibrary.urls')),
    path('', include('musicDatabase.urls')),
    path('', include('management.urls')),
    path('', include('cart.urls')),
    path('', include('crateBuilder.urls')),
    path('', include('members.urls')),
    path('', include('professionalServices.urls')),
    path('', include('shoppingCart.urls')),
    path('', include('vinylShop.urls')),
    path('', include('django.contrib.auth.urls')),
]
