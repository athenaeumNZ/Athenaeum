from django.urls import path

from shoppingCart import views

urlpatterns = [
    path('add_release_to_cart/<int:library_id>', views.add_release_to_cart, name='add_release_to_cart'),  
    path('remove_vinyl_release_from_shopping_cart/<int:library_id>', views.remove_vinyl_release_from_shopping_cart, name='remove_vinyl_release_from_shopping_cart'),
    path('shopping_cart/<int:library_id>', views.shopping_cart, name='shopping_cart'),
    path('shopping_cart_submission/<int:library_id>', views.shopping_cart_submission, name='shopping_cart_submission'),
]

''' UNUSED
    path('shopping_cart_from_plate_sorter/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>>&<str:display_searched_releases>', views.shopping_cart_from_plate_sorter, name='shopping_cart_from_plate_sorter'),
    path('shopping_cart_from_plate_sorter_remove_item_submission/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>>&<str:display_searched_releases>', views.shopping_cart_from_plate_sorter_remove_item_submission, name='shopping_cart_from_plate_sorter_remove_item_submission'),
    path('shopping_cart_add_item/<int:library_id>&<int:stock_item_id>', views.shopping_cart_add_item, name='shopping_cart_add_item'),
    path('shopping_cart_remove_item/<int:library_id>&<int:stock_item_id>', views.shopping_cart_remove_item, name='shopping_cart_remove_item'),
'''