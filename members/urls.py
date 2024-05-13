from django.urls import path
from . import views

urlpatterns = [
    
    path('member_address_print_out/<int:library_id>&<int:member_id>', views.member_address_print_out, name='member_address_print_out'),

    path('member_dashboard/<int:library_id>', views.member_dashboard, name='member_dashboard'),
    path('return_to_member_dashboard/<int:library_id>&<int:member_id>', views.return_to_member_dashboard, name='return_to_member_dashboard'),    
    path('order_request_item_hidden_from_member_submission/<int:library_id>&<int:order_request_item_id>', views.order_request_item_hidden_from_member_submission, name='order_request_item_hidden_from_member_submission'),    



    ############### members ###############
    # members
    path('members/<int:library_id>', views.members, name='members'),    
    ############### member crates ###############
    
    path('member_stockpile_submission/<int:library_id>', views.member_stockpile_submission, name='member_stockpile_submission'),  
    # member crate add
    path('member_crate_add/<int:library_id>&<int:member_id>', views.member_crate_add, name='member_crate_add'),
    # member crate add submission
    path('member_crate_add_submission/<int:library_id>', views.member_crate_add_submission, name='member_crate_add_submission'),
    # member crate add and move submission
    path('member_crate_add_and_move_submission/<int:library_id>&<int:plate_id>', views.member_crate_add_and_move_submission, name='member_crate_add_and_move_submission'),

    # member credit account
    path('member_credit_account/<int:library_id>&<int:member_id>', views.member_credit_account, name='member_credit_account'),
    # member crate add submission
    path('member_credit_account_submission/<int:library_id>&<int:member_id>', views.member_credit_account_submission, name='member_credit_account_submission'),

    # members crates
    path('members_crates/<int:library_id>&<int:member_id>', views.members_crates, name='members_crates'),
    # member default crates add 
    path('member_default_crates_add/<int:library_id>&<int:member_id>', views.member_default_crates_add, name='member_default_crates_add'),
    # member en route crate
    path('member_en_route_crate/<int:library_id>&<int:member_id>', views.member_en_route_crate, name='member_en_route_crate'),
    # member plate move
    path('member_plate_move/<int:library_id>&<int:sub_crate_id>&<int:plate_id>&<str:previous_url>', views.member_plate_move, name='member_plate_move'),
    # member plate move submission
    path('member_plate_move_submission/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.member_plate_move_submission, name='member_plate_move_submission'),
    
    # member plate advanced move submission
    path('member_plate_advanced_move_submission/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.member_plate_advanced_move_submission, name='member_plate_advanced_move_submission'),

    path('member_plate_swap_stock_for_incoming_stock/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.member_plate_swap_stock_for_incoming_stock, name='member_plate_swap_stock_for_incoming_stock'),

    path('member_plate_swap_stock_for_incoming_stock_and_delete_member_plate/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.member_plate_swap_stock_for_incoming_stock_and_delete_member_plate, name='member_plate_swap_stock_for_incoming_stock_and_delete_member_plate'),

    # member plates search
    path('member_limbo_crate_search/<int:library_id>&<int:member_id>', views.member_limbo_crate_search, name='member_limbo_crate_search'),
    
    # member stockpile
    path('member_stockpile/<int:library_id>&<int:member_id>', views.member_stockpile, name='member_stockpile'),

    # return to member limbo crate
    path('return_to_member_limbo_crate/<int:library_id>&<int:member_id>', views.return_to_member_limbo_crate, name='return_to_member_limbo_crate'),
    # return to member stockpile crate
    path('return_to_member_stockpile_crate/<int:library_id>&<int:member_id>', views.return_to_member_stockpile_crate, name='return_to_member_stockpile_crate'),
    # release add to members maybe list
    path('release_add_to_members_maybe_list_submission/<int:library_id>&<int:release_id>&<int:member_id>&<str:previous_url>', views.release_add_to_members_maybe_list_submission, name='release_add_to_members_maybe_list_submission'),
    # release remove from members maybe list
    path('release_remove_from_members_maybe_list_submission/<int:library_id>&<int:release_id>&<int:member_id>&<str:previous_url>', views.release_remove_from_members_maybe_list_submission, name='release_remove_from_members_maybe_list_submission'),
    # release add to members unwanted list
    path('release_add_to_members_unwanted_list_submission/<int:library_id>&<int:release_id>&<int:member_id>&<str:previous_url>', views.release_add_to_members_unwanted_list_submission, name='release_add_to_members_unwanted_list_submission'),
    # release remove from members unwanted list
    path('release_remove_from_members_unwanted_list_submission/<int:library_id>&<int:release_id>&<int:member_id>&<str:previous_url>', views.release_remove_from_members_unwanted_list_submission, name='release_remove_from_members_unwanted_list_submission'),
    # return to member stockpile crate
    path('release_add_to_members_wantlist_submission/<int:library_id>&<int:release_id>&<int:member_id>&<str:previous_url>', views.release_add_to_members_wantlist_submission, name='release_add_to_members_wantlist_submission'),
    # return to member stockpile crate
    path('release_remove_to_members_wantlist_submission/<int:library_id>&<int:release_id>&<int:member_id>&<str:previous_url>', views.release_remove_to_members_wantlist_submission, name='release_remove_to_members_wantlist_submission'),


]

''' unused
    # member plate move to en route crate submission
    path('member_plate_move_to_en_route_submission/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.member_plate_move_to_en_route_submission, name='member_plate_move_to_en_route_submission'),
    # member plate move to limbo crate submission
    path('member_plate_move_to_limbo_submission/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.member_plate_move_to_limbo_submission, name='member_plate_move_to_limbo_submission'),
    # member limbo crate
    path('member_limbo_crate/<int:library_id>&<int:member_id>', views.member_limbo_crate, name='member_limbo_crate'),

    # member plates
    path('member_personal_plates/<int:library_id>&<int:member_id>', views.member_personal_plates, name='member_personal_plates'),
    # member plates search
    path('member_personal_plates_search/<int:library_id>&<int:member_id>', views.member_personal_plates_search, name='member_personal_plates_search'),
'''