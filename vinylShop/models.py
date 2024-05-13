from django.db import models
from choices.models import Genre
from management.models import GenreOld, Library
from musicDatabase.models import VinylRelease

#region redundant
class WeeklyReleaseSheet(models.Model):
    search_start_date = models.DateField(blank=True, null=True)
    search_end_date = models.DateField(blank=True, null=True)
    printable_release_sheet = models.FileField(upload_to='static/vinylShop/weeklyReleaseSheet', blank=True)
    release_sheet_finalized = models.BooleanField(default=False)

    def __str__(self):
        return str(self.search_end_date)
    class Meta:
        ordering = ['-search_end_date']
#endregion
        
class StockItem(models.Model):
    vinyl_release = models.ForeignKey(VinylRelease, on_delete=models.PROTECT, related_name="vinyl_release_stock_item")
    library = models.ForeignKey(Library, on_delete=models.PROTECT)
    added = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveIntegerField(default=0) #this is used for the at stock athenaeum list. Won't be needed.
    #region adding a stock item
    added_by_member = models.BooleanField(default=False)
    updated_by_library_shop = models.BooleanField(default=False)
    in_library_shop_want_list = models.BooleanField(default=False)
    #endregion

    #region quantity
    quantity = models.IntegerField(default=0)
    has_an_outer_sleeve = models.BooleanField(default=False)
    quantity_incoming = models.IntegerField(default=0)
    quantity_plus_quantity_incoming_stock = models.IntegerField(default=0)
    #endregion
    #region auto restock
    auto_restock = models.BooleanField(default=False)
    auto_restock_threshold = models.PositiveIntegerField(default=1)
    auto_restock_quantity = models.PositiveIntegerField(default=1)
    #endregion
    unavailable = models.BooleanField(default=False)
    
    class Meta:
       unique_together = ("library", "vinyl_release",)
    
    def __str__(self):
        return str(self.vinyl_release)
    
class ShopGenre(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, null=True)
    library = models.ForeignKey(Library, on_delete=models.PROTECT)
       
    class Meta:
        ordering = ['genre']
        unique_together = ("library", "genre",)

    def __str__(self):
        return str(self.genre)
