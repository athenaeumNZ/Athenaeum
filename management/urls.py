from django.urls import path
from management import views

urlpatterns = [
    ############### crate database ###############
    # crate add
    path('crate_add/<int:library_id>', views.crate_add, name='crate_add'),
    # crate add submission
    path('crate_add_submission/<int:library_id>', views.crate_add_submission, name='crate_add_submission'),
    # crate database
    path('crate_database/<int:library_id>', views.crate_database, name='crate_database'),
    # crate database search
    path('crate_database_search/<int:library_id>', views.crate_database_search, name='crate_database_search'),
    # crate delete
    path('crate_delete/<int:library_id>&<int:crate_id>', views.crate_delete, name='crate_delete'),
    # crate delete submission
    path('crate_delete_submission/<int:library_id>&<int:crate_id>', views.crate_delete_submission, name='crate_delete_submission'),
    # crate edit
    path('crate_edit/<int:library_id>&<int:crate_id>', views.crate_edit, name='crate_edit'),
    # crate edit submission
    path('crate_edit_submission/<int:library_id>&<int:crate_id>', views.crate_edit_submission, name='crate_edit_submission'),
    # return to crate database
    path('return_to_crate_database/<int:library_id>', views.return_to_crate_database, name='return_to_crate_database'),

    ############### libraries ###############
    # library default crates add
    path('library_default_crates_add/<int:library_id>', views.library_default_crates_add, name='library_default_crates_add'), 
    # libraries
    path('libraries/', views.libraries, name='libraries'),





    ############### log in ###############
    path('log_in/', views.log_in, name='log_in'),
    path('log_in_backend/', views.log_in_backend, name='log_in_backend'),
    path('logged_in/', views.logged_in, name='logged_in'),

    ############### log out ###############
    path('log_out/', views.log_out, name='log_out'),
    path('logged_out/', views.log_out, name='logged_out'),


]