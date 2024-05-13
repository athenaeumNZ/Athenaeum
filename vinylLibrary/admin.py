from django.contrib import admin
from .models import *

class CrateIssueAdmin(admin.ModelAdmin):
    list_display = ('sub_crate', 'issue_date', 'expiry_date', 'status')
admin.site.register(CrateIssue, CrateIssueAdmin)

class LibraryCrateAdmin(admin.ModelAdmin):
    list_display = ('library_crate_id', 'library', 'date_created')
admin.site.register(LibraryCrate, LibraryCrateAdmin)

class LibraryPlateAdmin(admin.ModelAdmin):
    list_display = ('related_vinyl_plate', 'related_library_crate', 'related_sub_crate','date_added', 'contributor')
    search_fields = ['related_vinyl_plate__related_release__catalog_number']
admin.site.register(LibraryPlate, LibraryPlateAdmin)

class LibrarySubCrateAdmin(admin.ModelAdmin):
    list_display = ('sub_crate_id', 'master_library_crate', 'issued', 'crate_type')
admin.site.register(SubCrate, LibrarySubCrateAdmin)

admin.site.register(ReturnCrate)
