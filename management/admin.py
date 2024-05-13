from django.contrib import admin

from professionalServices.models import ProfessionalServiceProviderService
from vinylLibrary.models import Librarian
from .models import *

admin.site.register(Crate)


admin.site.register(Address)

class ProfessionalServiceProviderServiceInline(admin.TabularInline):
    model = ProfessionalServiceProviderService
    list_display = ['professional_service_type', 'fee_nzd', 'notes',]
    extra = 0


class LibrarianInline(admin.TabularInline):
    model = Librarian
    list_display = ['member',]
    extra = 0

class LibraryAdmin(admin.ModelAdmin):
    inlines = [LibrarianInline,]

admin.site.register(Library, LibraryAdmin)

class LibraryShopBlockedLabelsInline(admin.TabularInline):
    model = LibraryShopBlockedLabels
    list_display = ['member', 'label_name',]
    extra = 0

class MemberAdmin(admin.ModelAdmin):
    inlines = [ProfessionalServiceProviderServiceInline, LibraryShopBlockedLabelsInline,]
    
admin.site.register(Member, MemberAdmin)
admin.site.register(VinylDistributor)
admin.site.register(VinylShipping)
admin.site.register(Currency)
admin.site.register(Country)
admin.site.register(VinylColour)
admin.site.register(VinylIndex)
admin.site.register(VinylPlateSize)
admin.site.register(VinylSleeveType)
admin.site.register(VinylReleaseType)
admin.site.register(VinylCondition)
admin.site.register(GenreOld)
admin.site.register(Vibe)
admin.site.register(EnergyLevel)