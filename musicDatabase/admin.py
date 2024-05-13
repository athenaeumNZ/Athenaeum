from django.contrib import admin
from .models import *

class VinylReleaseAdmin(admin.ModelAdmin):
    list_display = ('catalog_number', 'artist', 'release_title', 'label', 'repress_request_count', 'plate_count', 'distributor',)
    readonly_fields = ['repress_request_count',]
    list_filter = ['distributor',]
    search_fields = ['catalog_number', 'label',]
admin.site.register(VinylRelease, VinylReleaseAdmin)

class VinylTrackAdmin(admin.ModelAdmin):
    list_display = ('related_vinyl_plate', 'index', 'artist', 'title', 'genre', 'vibe', 'energy_level')
admin.site.register(VinylTrack, VinylTrackAdmin)

class VinylPlateAdmin(admin.ModelAdmin):
    search_fields = ['related_release__catalog_number',]
admin.site.register(VinylPlate, VinylPlateAdmin)

admin.site.register(ArtistWrittenAs)

admin.site.register(VinylReleaseRepressRequest)
