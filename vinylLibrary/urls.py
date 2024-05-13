from django.urls import path
from vinylLibrary import views

urlpatterns = [
    path('', views.index, name='index'), 
    
    ############### issue crate ################
    # issue crate
    path('issue_crate/<int:library_id>&<int:sub_crate_id>', views.issue_crate,name='issue_crate'),
    # issue crate submission
    path('issue_crate_submission/<int:library_id>&<int:sub_crate_id>', views.issue_crate_submission, name='issue_crate_submission'),

    ############### library details ################
    # library details
    path('library_details/<int:library_id>', views.library_details, name='library_details'),

    ################ library crates ################
    # crates
    path('crates/<int:library_id>&<int:member_id>', views.crates, name='crates'),
    # library crate add
    path('library_crate_add/<int:library_id>', views.library_crate_add, name='library_crate_add'),
    # library crate add submission
    path('library_crate_add_submission/<int:library_id>', views.library_crate_add_submission, name='library_crate_add_submission'),
    # library crate delete
    path('library_crate_delete/<int:library_id>&<int:library_crate_id>', views.library_crate_delete, name='library_crate_delete'),
    # library crate delete submission
    path('library_crate_delete_submission/<int:library_id>&<int:library_crate_id>', views.library_crate_delete_submission, name='library_crate_delete_submission'),
    # library crate search --- need to update
    path('library_crate_search_by_crate_id/<int:library_id>', views.library_crate_search_by_crate_id, name='library_crate_search_by_crate_id'), 
    # library crate search --- need to update
    path('library_crate_search_by_crate_name/<int:library_id>', views.library_crate_search_by_crate_name, name='library_crate_search_by_crate_name'), 
    # return to crates
    path('return_to_crates/<int:library_id>', views.return_to_crates, name='return_to_crates'),
    
    ################ library plate ################
    # library plate add select plate
    path('library_plate_add_select_plate/<int:library_id>&<int:library_crate_id>&<int:sub_crate_id>', views.library_plate_add_select_plate, name='library_plate_add_select_plate'),
    # library plate add select plate catalog search
    path('library_plate_add_select_plate_catalog_search/<int:library_id>&<int:library_crate_id>&<int:sub_crate_id>', views.library_plate_add_select_plate_catalog_search, name='library_plate_add_select_plate_catalog_search'),
    # library plate add
    path('library_plate_add/<int:library_id>&<int:library_crate_id>&<int:sub_crate_id>&<int:vinyl_plate_id>', views.library_plate_add, name='library_plate_add'),
    #library plate add submission
    path('library_plate_add_submission/<int:library_id>&<int:library_crate_id>&<int:sub_crate_id>', views.library_plate_add_submission, name='library_plate_add_submission'), 
    # library plate delete
    path('library_plate_delete/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.library_plate_delete, name='library_plate_delete'),
    # library plate delete submission
    path('library_plate_delete_submission/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.library_plate_delete_submission, name='library_plate_delete_submission'), 
    # library plate edit
    path('library_plate_edit/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.library_plate_edit, name='library_plate_edit'),
    # library plate edit submission
    path('library_plate_edit_submission/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.library_plate_edit_submission, name='library_plate_edit_submission'), 
    # library plate move
    path('library_plate_move/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.library_plate_move, name='library_plate_move'),
    # library plate move submission
    path('library_plate_move_submission/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.library_plate_move_submission, name='library_plate_move_submission'),
    # library plate printing
    path('library_plate_printing_page/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.library_plate_printing_page, name='library_plate_printing_page'),
    # library plates printing all
    path('library_plate_printing_all_page/<int:library_id>&<int:sub_crate_id>', views.library_plate_printing_all_page, name='library_plate_printing_all_page'),


         
    ################ return crate ################
    path('return_crate/<int:library_id>&<int:sub_crate_id>', views.return_crate, name='return_crate'),
    path('return_crate_submission/<int:library_id>&<int:sub_crate_id>', views.return_crate_submission, name='return_crate_submission'),
    



    ################ sub crates ################
    # return to sub crate
    path('return_to_sub_crate/<int:library_id>&<int:library_crate_id>&<int:sub_crate_id>', views.return_to_sub_crate, name='return_to_sub_crate'),
    # sub crate
    path('sub_crate/<int:library_id>&<int:sub_crate_id>&<int:member_id>', views.sub_crate, name='sub_crate'),
    # sub crate add
    path('sub_crate_add/<int:library_id>&<int:library_crate_id>', views.sub_crate_add, name='sub_crate_add'),
    # sub crate add submission
    path('sub_crate_add_submission/<int:library_id>&<int:library_crate_id>', views.sub_crate_add_submission, name='sub_crate_add_submission'),
    # sub crate delete
    path('sub_crate_delete/<int:library_id>&<int:sub_crate_id>&<int:member_id>', views.sub_crate_delete, name='sub_crate_delete'),
    # sub crate delete submission
    path('sub_crate_delete_submission/<int:library_id>&<int:sub_crate_id>&<int:member_id>', views.sub_crate_delete_submission, name='sub_crate_delete_submission'),
    # sub crate edit
    path('sub_crate_edit/<int:library_id>&<int:library_crate_id>&<int:sub_crate_id>', views.sub_crate_edit, name='sub_crate_edit'),
    # sub crate edit submission
    path('sub_crate_edit_submission/<int:library_id>&<int:library_crate_id>&<int:sub_crate_id>', views.sub_crate_edit_submission, name='sub_crate_edit_submission'),
    # sub_crate search
    path('sub_crate_search/<int:library_id>&<int:library_crate_id>&<int:sub_crate_id>&<int:member_id>', views.sub_crate_search, name='sub_crate_search'),
    # trade plate move 
    path('trade_plate_move/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.trade_plate_move, name='trade_plate_move'),
    # trade plate move submission
    path('trade_plate_move_submission/<int:library_id>&<int:sub_crate_id>&<int:plate_id>', views.trade_plate_move_submission, name='trade_plate_move_submission'),
    # sub crate printing
    path('sub_crate_divider_insert_printing/<int:library_id>&<int:sub_crate_id>', views.sub_crate_divider_insert_printing, name='sub_crate_divider_insert_printing'),
    ]

''' barcodes
    path('make_lots_of_barcodes/', views.make_lots_of_barcodes, name='make_lots_of_barcodes'),
    path('make_lots_of_crate_barcodes/', views.make_lots_of_crate_barcodes, name='make_lots_of_crate_barcodes'),

'''