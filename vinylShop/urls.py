from django.urls import path
from vinylShop import views

urlpatterns = [
    #''' REDUNDANT ->'''
    #region personal weekly releases
    path('personal_weekly_releases/<int:library_id>&<int:member_id>', views.personal_weekly_releases, name='personal_weekly_releases'),
    #endregion
    #region vinyl ordering
    path('return_to_vinyl_ordering/<int:library_id>', views.return_to_vinyl_ordering, name='return_to_vinyl_ordering'),    
    path('vinyl_ordering/<int:library_id>', views.vinyl_ordering, name='vinyl_ordering'), 
    path('vinyl_ordering_search/<int:library_id>', views.vinyl_ordering_search, name='vinyl_ordering_search'),
    path('update_distributors_stock_submission/<int:library_id>', views.update_distributors_stock_submission, name='update_distributors_stock_submission'), 
    #endregion
    #region weekly releases
    path('return_to_weekly_release_sheets/<int:library_id>', views.return_to_weekly_release_sheets, name='return_to_weekly_release_sheets'),
    path('weekly_release_sheets/<int:library_id>', views.weekly_release_sheets, name='weekly_release_sheets'),
    path('weekly_releases/<int:library_id>&<int:weekly_release_sheet_id>', views.weekly_releases, name='weekly_releases'),
    path('weekly_releases_set_to_on_previous_release_sheet_submission/<int:library_id>&<int:weekly_release_sheet_id>&<str:search_start_date>&<str:search_end_date>', views.weekly_releases_set_to_on_previous_release_sheet_submission, name='weekly_releases_set_to_on_previous_release_sheet_submission'),
    path('weekly_release_sheet_add/<int:library_id>', views.weekly_release_sheet_add, name='weekly_release_sheet_add'),
    path('weekly_release_sheet_add_submission/<int:library_id>', views.weekly_release_sheet_add_submission, name='weekly_release_sheet_add_submission'),
    path('weekly_release_sheet_edit/<int:library_id>&<int:weekly_release_sheet_id>', views.weekly_release_sheet_edit, name='weekly_release_sheet_edit'),
    path('weekly_release_sheet_edit_submission/<int:library_id>&<int:weekly_release_sheet_id>', views.weekly_release_sheet_edit_submission, name='weekly_release_sheet_edit_submission'),    
    path('weekly_release_sheet_upload/<int:library_id>&<int:weekly_release_sheet_id>', views.weekly_release_sheet_upload, name='weekly_release_sheet_upload'),
    path('weekly_release_sheet_upload_submission/<int:library_id>&<int:weekly_release_sheet_id>', views.weekly_release_sheet_upload_submission, name='weekly_release_sheet_upload_submission'),
    #endregion
    #'''<- <- REDUNDANT '''
    path('stock_item_add_edit_order_submission/', views.stock_item_add_edit_order_submission, name='stock_item_add_edit_order_submission'),
    
    #region vinyl shop
    path('return_to_stock_item_add_edit_select/<int:library_id>', views.return_to_stock_item_add_edit_select, name='return_to_stock_item_add_edit_select'),    
    path('stock_item_add_edit_select/<int:library_id>', views.stock_item_add_edit_select, name='stock_item_add_edit_select'),
    path('stock_item_add_edit_select_search/<int:library_id>', views.stock_item_add_edit_select_search, name='stock_item_add_edit_select_search'),
    path('stock_item_add_edit/<int:library_id>&<int:release_id>', views.stock_item_add_edit, name='stock_item_add_edit'), 
    path('stock_item_delete_submission/<int:library_id>&<int:stock_item_id>', views.stock_item_delete_submission, name='stock_item_delete_submission'), 
    path('stock_item_member_add_submission/<int:library_id>&<int:release_id>', views.stock_item_member_add_submission, name='stock_item_member_add_submission'), 
    path('stock_item_add_edit_submission/<int:library_id>&<int:release_id>', views.stock_item_add_edit_submission, name='stock_item_add_edit_submission'), 
    path('return_to_vinyl_shop/<int:library_id>', views.return_to_vinyl_shop, name='return_to_vinyl_shop'),    
    path('vinyl_shop/<int:library_id>', views.vinyl_shop, name='vinyl_shop'),

    path('vinyl_shop_in_stock/<int:library_id>', views.vinyl_shop_in_stock, name='vinyl_shop_in_stock'),  
    path('vinyl_shop_in_stock_update_most_common_submission/<int:library_id>', views.vinyl_shop_in_stock_update_most_common_submission, name='vinyl_shop_in_stock_update_most_common_submission'),  
    path('return_to_vinyl_shop_in_stock/<int:library_id>', views.return_to_vinyl_shop_in_stock, name='return_to_vinyl_shop_in_stock'),  
    path('vinyl_shop_in_stock_update_status_submission/<int:library_id>', views.vinyl_shop_in_stock_update_status_submission, name='vinyl_shop_in_stock_update_status_submission'),  
    path('return_to_stock_item_add_edit/<int:library_id>&<int:vinyl_release_id>', views.return_to_stock_item_add_edit, name='return_to_stock_item_add_edit'),
    path('vinyl_shop_search/<int:library_id>', views.vinyl_shop_search, name='vinyl_shop_search'), 
    path('vinyl_shop_search_from_stock_add_edit/<int:library_id>', views.vinyl_shop_search_from_stock_add_edit, name='vinyl_shop_search_from_stock_add_edit'), 
    #endregion

    path('print_crate_divider_stockpile/<int:library_id>&<int:member_id>', views.print_crate_divider_stockpile, name='print_crate_divider_stockpile'), 

]

#region OLD
''' stock_item_add_all_from_librarian_stockpile_submission
    path('stock_item_add_all_from_librarian_stockpile_submission/<int:library_id>', views.stock_item_add_all_from_librarian_stockpile_submission, name='stock_item_add_all_from_librarian_stockpile_submission'),
'''
''' vinyl_shop_members_invoices
    # vinyl shop members invoices
    path('vinyl_shop_members_invoices/<int:library_id>&<int:member_id>', views.vinyl_shop_members_invoices, name='vinyl_shop_members_invoices'),

'''
''' return_to_vinyl_shop_members_invoices
    # return to vinyl shop members invoices
    path('return_to_vinyl_shop_members_invoices/<int:library_id>&<int:member_id>', views.return_to_vinyl_shop_members_invoices, name='return_to_vinyl_shop_members_invoices'),

'''
''' sale vinyl
#region sale vinyl ###############

    # return to sale vinyl option
    path('return_to_sale_vinyl_options/<int:library_id>&<int:release_id>', views.return_to_sale_vinyl_options, name='return_to_sale_vinyl_options'), 
    # sale vinyl add
    path('sale_vinyl_add_details/<int:library_id>&<int:release_id>', views.sale_vinyl_add_details, name='sale_vinyl_add_details'),
    # sale vinyl add details submission
    path('sale_vinyl_add_details_submission/<int:library_id>&<int:release_id>', views.sale_vinyl_add_details_submission, name='sale_vinyl_add_details_submission'), 
    # sale vinyl edit
    path('sale_vinyl_edit_details/<int:library_id>&<int:release_id>', views.sale_vinyl_edit_details, name='sale_vinyl_edit_details'),
    # sale vinyl edit submission
    path('sale_vinyl_edit_details_submission/<int:library_id>&<int:release_id>', views.sale_vinyl_edit_details_submission, name='sale_vinyl_edit_details_submission'), 
    # sale vinyl options
    path('sale_vinyl_options/<int:library_id>&<int:release_id>', views.sale_vinyl_options, name='sale_vinyl_options'), 

    #endregion
'''
''' old urls

    
    # pricing calculations
    path('pricing_calculations/<int:library_id>', views.pricing_calculations, name='pricing_calculations'),
    # sale vinyl calculate sale price nz
    path('sale_vinyl_calculate_sale_price_nz/<int:library_id>&<int:release_id>', views.sale_vinyl_calculate_sale_price_nz, name='sale_vinyl_calculate_sale_price_nz'), 
    path('sale_vinyl_calculate_sale_price_nz_submission/<int:library_id>&<int:release_id>', views.sale_vinyl_calculate_sale_price_nz_submission, name='sale_vinyl_calculate_sale_price_nz_submission'), 
    # wp order
    path('wp_order/<int:library_id>', views.wp_order, name='wp_order'),
    # wp order placed
    path('wp_order_placed/<int:library_id>', views.wp_order_placed, name='wp_order_placed'),
    # wp order
    path('kud_order/<int:library_id>', views.kud_order, name='kud_order'),
    # kud order placed
    path('kud_order_placed/<int:library_id>', views.kud_order_placed, name='kud_order_placed'),
    # vinyl shop add - select release
    path('vinyl_shop_add_select_release/<int:library_id>', views.vinyl_shop_add_select_release, name='vinyl_shop_add_select_release'),
    # vinyl shop add - select release search 
    path('vinyl_shop_add_select_release_catalog_search/<int:library_id>', views.vinyl_shop_add_select_release_catalog_search, name='vinyl_shop_add_select_release_catalog_search'),
    # vinyl shop add stock
    path('vinyl_shop_add_stock/<int:library_id>&<int:release_id>', views.vinyl_shop_add_stock, name='vinyl_shop_add_stock'),
    # vinyl shop add stock submission
    path('vinyl_shop_add_stock_submission/<int:library_id>&<int:release_id>&<str:previous_url>', views.vinyl_shop_add_stock_submission, name='vinyl_shop_add_stock_submission'),
    # triple vision order
    path('tvd_order/<int:library_id>', views.tvd_order, name='tvd_order'),
    # triple vision order placed
    path('tvd_order_placed/<int:library_id>', views.tvd_order_placed, name='tvd_order_placed'),  
    # ues order
    path('ues_order/<int:library_id>', views.ues_order, name='ues_order'),
    # ues order placed
    path('ues_order_placed/<int:library_id>', views.ues_order_placed, name='ues_order_placed'),    

    # no mark up price nz
    path('no_mark_up_price_nz/<int:library_id>&<int:release_id>', views.no_mark_up_price_nz, name='no_mark_up_price_nz'), 
    # no mark up price nz submission
    path('no_mark_up_price_nz_submission/<int:library_id>&<int:release_id>', views.no_mark_up_price_nz_submission, name='no_mark_up_price_nz_submission'), 

'''
''' external vinyl shop urls   

    # vinyl shop stock delete
    path('vinyl_shop_stock_delete/<int:library_id>&<int:library_sale_vinyl_id>', views.vinyl_shop_stock_delete, name='vinyl_shop_stock_delete'),
    # vinyl shop stock delete submission
    path('vinyl_shop_stock_delete_submission/<int:library_id>&<int:library_sale_vinyl_id>', views.vinyl_shop_stock_delete_submission, name='vinyl_shop_stock_delete_submission'),
    # vinyl shop stock edit
    path('vinyl_shop_stock_edit/<int:library_id>&<int:library_sale_vinyl_id>', views.vinyl_shop_stock_edit, name='vinyl_shop_stock_edit'),
    # vinyl shop stock edit
    path('vinyl_shop_stock_edit_submission/<int:library_id>&<int:library_sale_vinyl_id>', views.vinyl_shop_stock_edit_submission, name='vinyl_shop_stock_edit_submission'),'''

#endregion