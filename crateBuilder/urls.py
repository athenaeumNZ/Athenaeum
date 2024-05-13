from django.urls import path
from crateBuilder import views

urlpatterns = [

    path('member_plate_crate_parent_set/<int:library_id>', views.member_plate_crate_parent_set, name='member_plate_crate_parent_set'),
    path('plate_move/<int:library_id>', views.plate_move, name='plate_move'),
    path('plate_sorter/<int:library_id>', views.plate_sorter, name='plate_sorter'),
    path('member_release_create/<int:library_id>', views.member_release_create, name='member_release_create'),       
    path('stock_item_create_and_add_to_cart/<int:library_id>', views.stock_item_create_and_add_to_cart, name='stock_item_create_and_add_to_cart'),       

    
    

    path('plate_crate_parent_desired_option_set_submission/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>&<str:display_searched_releases>', views.plate_crate_parent_desired_option_set_submission, name='plate_crate_parent_desired_option_set_submission'),
    path('stock_item_member_add_and_return_to_plate_sorter_submission/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>&<str:display_searched_releases>', views.stock_item_member_add_and_return_to_plate_sorter_submission, name='stock_item_member_add_and_return_to_plate_sorter_submission'),
    path('crate_parent_create_submission/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>&<str:display_searched_releases>', views.crate_parent_create_submission, name='crate_parent_create_submission'),
    path('return_to_plate_sorter/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>&<str:display_searched_releases>', views.return_to_plate_sorter, name='return_to_plate_sorter'),        
    path('plate_move_submission/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>&<str:display_searched_releases>', views.plate_move_submission, name='plate_move_submission'),        
    path('member_release_create_submission/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>&<str:display_searched_releases>', views.member_release_create_submission, name='member_release_create_submission'),       
]

''' UNUSED
    path('plate_sorter_add_release_to_cart/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>&<str:display_searched_releases>', views.plate_sorter_add_release_to_cart, name='plate_sorter_add_release_to_cart'),
    path('plate_sorter_remove_release_from_cart/<int:library_id>&<int:member_id>&<str:crate_id>&<str:crate_parent_id>&<str:display_stock>&<str:display_unallocated>&<str:display_searched_releases>', views.plate_sorter_remove_release_from_cart, name='plate_sorter_remove_release_from_cart'),
'''