from django.urls import path
from musicDatabase import views

urlpatterns = [
    path('vinyl_release/<int:library_id>', views.vinyl_release, name='vinyl_release'),
    path('return_to_vinyl_release/<int:library_id>', views.return_to_vinyl_release, name='return_to_vinyl_release'), 









    #region release
    path('release/<int:library_id>&<int:release_id>', views.release, name='release'),
    path('release_request_repress_submission/<int:library_id>', views.release_request_repress_submission, name='release_request_repress_submission'),
    path('return_to_release/<int:library_id>&<int:release_id>', views.return_to_release, name='return_to_release'),
    
    #endregion

    #region release add
    path('vinyl_release_add_check_catalog_number/<int:library_id>', views.vinyl_release_add_check_catalog_number, name='vinyl_release_add_check_catalog_number'),
    path('vinyl_release_add_check_catalog_number_submission/<int:library_id>', views.vinyl_release_add_check_catalog_number_submission, name='vinyl_release_add_check_catalog_number_submission'),
    path('vinyl_release_add/<int:library_id>&<str:catalog_number>', views.vinyl_release_add, name='vinyl_release_add'),
    path('vinyl_release_add_submission/<int:library_id>', views.vinyl_release_add_submission, name='vinyl_release_add_submission'),
    #endregion

    #region release compile
    path('release_compile/<int:library_id>&<int:release_id>', views.release_compile, name='release_compile'),
    path('return_to_release_compile/<int:library_id>&<int:release_id>', views.return_to_release_compile, name='return_to_release_compile'),
    path('release_delete/<int:library_id>&<int:release_id>', views.release_delete, name='release_delete'),
    path('release_delete_submission/<int:library_id>&<int:release_id>', views.release_delete_submission, name='release_delete_submission'),
    path('release_edit/<int:library_id>&<int:release_id>&<str:catalog_number_to_check>', views.release_edit, name='release_edit'),
    path('release_edit_submission/<int:library_id>&<int:release_id>', views.release_edit_submission, name='release_edit_submission'),
    path('release_plate_add/<int:library_id>&<int:release_id>', views.release_plate_add, name='release_plate_add'),
    path('release_plate_add_submission/<int:library_id>&<int:release_id>', views.release_plate_add_submission, name='release_plate_add_submission'),
    path('release_plate_delete/<int:library_id>&<int:release_id>&<int:plate_id>', views.release_plate_delete, name='release_plate_delete'),
    path('release_plate_delete_submission/<int:library_id>&<int:release_id>&<int:plate_id>', views.release_plate_delete_submission, name='release_plate_delete_submission'),
    #endregion

    #region track
    path('return_to_track_add/<int:library_id>&<int:release_id>&<int:plate_id>', views.return_to_track_add, name='return_to_track_add'),
    path('return_to_track_categorize_next/<int:library_id>&<int:release_id>&<int:index_count>', views.return_to_track_categorize_next, name='return_to_track_categorize_next'),
    path('track_add/<int:library_id>&<int:release_id>&<int:plate_id>', views.track_add, name='track_add'),
    path('track_add_go_to_first_track_add/<int:library_id>&<int:release_id>&<int:plate_id>', views.track_add_go_to_first_track_add, name='track_add_go_to_first_track_add'),
    path('track_add_submission/<int:library_id>&<int:release_id>&<int:plate_id>', views.track_add_submission, name='track_add_submission'),
    path('track_audio_add<int:library_id>&<int:release_id>&<int:track_id>', views.track_audio_add, name='track_audio_add'),
    path('track_audio_add_submission/<int:library_id>&<int:release_id>&<int:track_id>', views.track_audio_add_submission, name='track_audio_add_submission'),
    path('track_categorize_first/<int:library_id>&<int:release_id>&<int:track_id>', views.track_categorize_first, name='track_categorize_first'),
    path('track_categorize_next/<int:library_id>&<int:release_id>&<int:index_count>', views.track_categorize_next, name='track_categorize_next'),
    path('track_categorize_submission/<int:library_id>&<int:release_id>&<int:track_id>&<int:index_count>', views.track_categorize_submission, name='track_categorize_submission'),
    path('track_delete/<int:library_id>&<int:release_id>&<int:track_id>', views.track_delete, name='track_delete'),
    path('track_delete_submission/<int:library_id>&<int:release_id>&<int:track_id>', views.track_delete_submission, name='track_delete_submission'),
    path('track_edit/<int:library_id>&<int:release_id>&<int:track_id>', views.track_edit, name='track_edit'),
    path('track_edit_submission/<int:library_id>&<int:release_id>&<int:track_id>', views.track_edit_submission, name='track_edit_submission'),
    #endregion
]

''' OLD
    # release database search
    path('release_database_search/<int:library_id>', views.release_database_search, name='release_database_search'),

    ############### release database ###############
    path('release_database/<int:library_id>&<int:member_id>', views.release_database, name='release_database'),
    path('return_to_release_database/<int:library_id>', views.return_to_release_database, name='return_to_release_database'),

    path('release_finalized_submission/<int:library_id>&<int:release_id>', views.release_finalized_submission, name='release_finalized_submission'),

    ############### artist naming conventions ###############
    path('artist_naming_conventions/<int:library_id>', views.artist_naming_conventions, name='artist_naming_conventions'),
    path('return_to_artist_naming_conventions/<int:library_id>', views.return_to_artist_naming_conventions, name='return_to_artist_naming_conventions'),

    # artist naming conventions add
    path('artist_naming_convention_add/<int:library_id>', views.artist_naming_convention_add, name='artist_naming_convention_add'),
    path('artist_naming_convention_add_submission/<int:library_id>', views.artist_naming_convention_add_submission, name='artist_naming_convention_add_submission'),
    
    # artist naming conventions delete
    path('artist_naming_convention_delete/<int:library_id>&<int:artist_written_as_id>', views.artist_naming_convention_delete, name='artist_naming_convention_delete'),
    path('artist_naming_convention_delete_submission/<int:library_id>&<int:artist_written_as_id>', views.artist_naming_convention_delete_submission, name='artist_naming_convention_delete_submission'),
   
    # artist naming conventions edit
    path('artist_naming_convention_edit/<int:library_id>&<int:artist_written_as_id>', views.artist_naming_convention_edit, name='artist_naming_convention_edit'),
    path('artist_naming_convention_edit_submission/<int:library_id>&<int:artist_written_as_id>', views.artist_naming_convention_edit_submission, name='artist_naming_convention_edit_submission'),
    
    # artist naming conventions search
    path('artist_naming_conventions_search/<int:library_id>', views.artist_naming_conventions_search, name='artist_naming_conventions_search'),
    path('release_add_bulk_submission/<int:library_id>', views.release_add_bulk_submission, name='release_add_bulk_submission'),

    # release plate and track count submission
    path('release_plate_and_track_count_submission/<int:library_id>&<int:release_id>', views.release_plate_and_track_count_submission, name='release_plate_and_track_count_submission'),

'''