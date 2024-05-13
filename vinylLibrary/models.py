from django.db import models
from django.db.models.fields import *

from musicDatabase.models import VinylRelease, VinylPlate
from management.models import Library, Crate, VinylColour, Member
from datetime import datetime,timedelta

def expiry():
        return datetime.today() + timedelta(days=22) 

def date_now():
        return datetime.today()

class CrateIssue(models.Model):
    RETURN_STATUS = (
        ('Issued', 'Issued'),
        ('Returned', 'Returned')
    )
    date_time_created = models.DateTimeField(auto_now_add=True)
    issue_date = models.DateField(default=date_now)
    expiry_date = models.DateField(default=expiry)
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    sub_crate = models.ForeignKey('SubCrate', on_delete=models.PROTECT)
    status = models.CharField(choices=RETURN_STATUS, max_length=20, default='Issued')
    def __str__(self):
        return str(self.sub_crate)

class LibraryCrate(models.Model):
    related_crate = models.ForeignKey(Crate, on_delete=models.PROTECT, blank=True, null=True)
    library = models.ForeignKey(Library, on_delete=models.PROTECT)
    library_crate_id = models.CharField(max_length=70, unique=True)
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_modified = models.DateField(auto_now=True)
    crate_type = models.CharField(max_length=70)
    def __str__(self):
        return self.library_crate_id
    class Meta:
        ordering = ['library_crate_id']

class LibraryPlate(models.Model):
    CONDITION = (
        ('G', 'Good'),
        ('VG', 'Very Good'),
        ('VG+', 'Very Good Plus'),
        ('NM', 'Near Mint'),
        ('M', 'Mint')
    )
    COVER = (
        ('Inner Sleeve', 'Inner Sleeve'),
        ('Full Artwork', 'Full Artwork'),
        ('Top Sticker Artwork', 'Top Sticker Artwork'),
        ('Record Label Sleeve', 'Record Label Sleeve'),
        ('Plain', 'Plain'),
    )   
    PLATE_SIZE = (
        ('12"', '12"'),
        ('10"', '10"'),
        ('7"', '7"'),
    )
    RELEASE_TYPE = (
        ('Full Release', 'Full Release'),
        ('White Label', 'White Label'),
        ('Stickered', 'Stickered'),
    )
    VINYL_COLOUR = (
        ('Black', 'Black'),
        ('Blue Marbled', 'Blue Marbled'),
        ('Blue Translucent', 'Blue Translucent'),
        ('Clear', 'Clear'),
        ('Gold', 'Gold'),
        ('Grey Marbled', 'Grey Marbled'),
        ('Magenta Translucent', 'Magenta Translucent'),	
        ('Orange Translucent', 'Orange Translucent'),
        ('Purple Marbled', 'Purple Marbled'),
        ('Red', 'Red'),
        ('Silver', 'Silver'),
        ('White', 'White')
    )
    
    related_vinyl_plate = models.ForeignKey(VinylPlate, on_delete=models.PROTECT)
    related_library_crate = models.ForeignKey('LibraryCrate', on_delete=models.PROTECT, related_name='related_library_plate')    
    related_sub_crate = models.ForeignKey('SubCrate', on_delete=models.PROTECT, related_name='related_library_plate', blank=True, null=True)
    contributor = models.ForeignKey(Member, on_delete=models.PROTECT)
    cover = models.CharField(choices=COVER, max_length=100, blank=True) # remove blank later
    plate_size = models.CharField(choices=PLATE_SIZE, max_length=70)    
    release_type = models.CharField(choices=RELEASE_TYPE, blank=True, max_length=100) # remove blank later
    media_condition = models.CharField(max_length=20, choices=CONDITION, blank=True)
    vinyl_colour = models.CharField(max_length=100, null=True, blank=True) # remove null and blank later
    date_added = models.DateField(auto_now_add=True)
    barcode = models.ImageField(upload_to='static/vinylLibrary/libraryPlatesBarcodes', blank=True)
    date_time_created = models.DateTimeField(auto_now_add=True)
    recieved = models.BooleanField(default=False)
    paid_for = models.BooleanField(default=False)

    def __str__(self):
        return str(self.related_vinyl_plate)
    class Meta:
            ordering = ['related_vinyl_plate']

''' LibrarySaleVinyl
class LibrarySaleVinyl(models.Model):
    related_release = models.ForeignKey(VinylRelease, on_delete=models.PROTECT, related_name='related_library_sale_vinyl')
    library = models.ForeignKey(Library, on_delete=models.PROTECT)
    stock = models.PositiveIntegerField()
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)

    def __str__(self):
        return str(self.related_release)
'''

class ReturnCrate(models.Model):
    library_crate = models.CharField(max_length=20)

class SubCrate(models.Model):
    ISSUE_STATUS = (
        ('Issued', 'Issued'),
        ('Available', 'Available')
    )
    RESERVE_STATUS = (
        ('Reserved', 'Reserved'),
        ('Available', 'Available')
    )
    master_library_crate = models.ForeignKey(LibraryCrate, on_delete=models.PROTECT, related_name='sub_crates')
    crate_index_start = models.CharField(max_length=20, default='A')
    crate_index_end = models.CharField(max_length=20, default='Z')
    plate_count = models.CharField(max_length=20, default='0')
    crate_type = models.CharField(max_length=70)
    sub_crate_id = models.CharField(max_length=70, unique=True)
    issued = models.CharField(choices=ISSUE_STATUS, max_length=20, default='Available')
    reserved = models.CharField(choices=RESERVE_STATUS, max_length=12, default='Available')
    barcode = models.ImageField(upload_to='static/vinylLibrary/librarySubCrateBarcodes', blank=True)

    def __str__(self):
        return self.sub_crate_id
    class Meta:
        ordering = ['sub_crate_id']

class Librarian(models.Model):
    library = models.ForeignKey(Library, on_delete=models.PROTECT, related_name='librarian_library')
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='librarian_member')
    
    class Meta:
        ordering = ['library', 'member',]

    def __str__(self):
        return str(self.member)
    