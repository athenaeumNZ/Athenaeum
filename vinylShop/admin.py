from django.contrib import admin

from vinylShop.models import ShopGenre, StockItem, WeeklyReleaseSheet

admin.site.register(ShopGenre)
class StockItemAdmin(admin.ModelAdmin):
    search_fields = ['vinyl_release__catalog_number',]
    list_display = ['vinyl_release', 'price',]
admin.site.register(StockItem, StockItemAdmin)






''' REDUNDANT ->'''
class WeeklyReleaseSheetAdmin(admin.ModelAdmin):
    list_display = ('search_end_date', 'search_start_date')
admin.site.register(WeeklyReleaseSheet, WeeklyReleaseSheetAdmin)
'''<- <- REDUNDANT '''