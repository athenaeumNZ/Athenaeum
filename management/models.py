from decimal import Decimal
from django.db import models
from django.db.models.fields import *
# from datetime import datetime, timedelta
# from musicDatabase.models import *
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

from accounts.models import *


class Crate(models.Model):
    ENERGY_LEVEL = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6')
    )
    GENRE = (
        ('DnB', 'DnB'),
        ('Jungle 94-00', 'Jungle 94-00'),
        ('Jungle 10-', 'Jungle 10-'),
        ('Dubstep', 'Dubstep'),
        ('Grime', 'Grime'),
        ('DnB Liquid', 'DnB Liquid'),
        ('Neurofunk 04-', 'NeuroFunk 04-'),
        ('Neurofunk 98-03', 'NeuroFunk 98-03'),
        ('DnB Minimal', 'DnB Minimal'),
        ('Halftime', 'Halftime'),
        ('Eclectic', 'Eclectic')
    )
    VIBE = (
        ('Yellow', 'Yellow'),
        ('Blue', 'Blue'),
        ('Red', 'Red'),
        ('Green', 'Green'),
    )
    crate_id = models.CharField(max_length=20)
    description = models.CharField(max_length=150, default='')
    energy_level = models.CharField(choices=ENERGY_LEVEL, null=True, blank=True , max_length=20)
    genre = models.CharField(choices=GENRE, max_length=50, null=True, blank=True )
    mix = models.FileField(upload_to='static/management/crateMixes', blank=True)
    vibe = models.CharField(choices=VIBE, max_length=20, null=True, blank=True )
    def __str__(self):
        return str(self.crate_id)
    class Meta:
        ordering = ['crate_id']

class Library(models.Model):
    YES_NO = (
        ('No', 'No'),
        ('Yes', 'Yes')
    )
    FREQUENCY = (
        ('Before Use','Before Use'),
        ('After Use','After Use'),
        ('Daily', 'Daily'),
        ('Twice a week', 'Twice a week'),
        ('Once a week', 'Once a week'),
        ('Fortnightly', 'Fortnightly'),
        ('Monthly','Monthly'),
        ('Never','Never')
    )

    #region basic details
    name = models.CharField(max_length=100)
    library_shop = models.ForeignKey(User, on_delete=models.CASCADE, related_name="library_library_shop", blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True)
    date_established = models.DateField(auto_now_add=True)
    logo_black_on_white = models.FileField(upload_to='static/vinyllibrary/librarylogos', blank=True)
    logo_white_on_black = models.FileField(upload_to='static/vinyllibrary/librarylogos', blank=True)
    #endregion
    #region address
    unit_number = models.CharField(max_length=10, blank=True)
    street_number = models.CharField(max_length=10, blank=True)
    street_name = models.CharField(max_length=100, blank=True)
    suburb = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    #endregion
    #region money
    currency = models.CharField(max_length=20)
    gst = models.CharField(max_length=20)
    #endregion
    
    #region specifications
    # plates
    cue_points = models.CharField("All plates have Maxwell cue points?", default='Yes', max_length=20, choices=YES_NO)
    sleeve_catalog = models.CharField("All outersleeves have catalog number sticker on top?", default='Yes', max_length=20, choices=YES_NO)
    info_sheet = models.CharField("All plates come with Maxwell cover sheet?", default='Yes', max_length=20, choices=YES_NO)
    plate_stickers = models.CharField("All plates have non cue point stickers removed?", default='Yes', max_length=20, choices=YES_NO)
    outersleeve_stickers = models.CharField("All outersleeves have stickers removed?", default='Yes', max_length=20, choices=YES_NO)

    # Record playing rules
    finger_nails = models.CharField("Members finger nails must be trimmed and filed?", default='Yes', max_length=20, choices=YES_NO)
    records_playable = models.CharField("Records can be played?", default='Yes', max_length=20, choices=YES_NO)
    records_mixable = models.CharField("Records can be mixed?", default='Yes', max_length=20, choices=YES_NO)
    non_members = models.CharField("Only members can play or handle or mix records?", default='Yes', max_length=20, choices=YES_NO)
    outdoor_playing = models.CharField("Records can be played outdoors?", default='No', max_length=20, choices=YES_NO)

    # library_cleaning
    library_cleanroom = models.CharField("Environment is a classified cleanroom?", default='No', max_length=20, choices=YES_NO)
    library_controled_temperature = models.CharField("Library has 24/7 365 temperature control?", default='Yes', max_length=20, choices=YES_NO) 
    library_dry_wipe_tops_of_crates = models.CharField(choices=FREQUENCY, max_length=100, default='Before Use')
    library_dry_wiped = models.CharField(choices=FREQUENCY, max_length=100, default='Once a week')
    library_smoking = models.CharField("Smoking is allowed in the library?", default='No', max_length=20, choices=YES_NO)
    library_gloves =  models.CharField("Cotton Gloves are required when handeling records?", default='No', max_length=20, choices=YES_NO)
    library_thoroughfare = models.CharField("Library is located in a thoroughfare?", default='No', max_length=20, choices=YES_NO)
    library_turntables_dusted_and_vacummed = models.CharField(choices=FREQUENCY, max_length=100, default='Before Use')
    library_vacuumed = models.CharField(choices=FREQUENCY, max_length=100, default='Once a week')
    library_vestibule = models.CharField("Library has a dust control vestibule?", default='No', max_length=20, choices=YES_NO)
    library_wet_wiped = models.CharField(choices=FREQUENCY, max_length=100, default='Fortnightly')

    #studio_cleaning
    studio_cleanroom = models.CharField("Studio is a classified cleanroom?", default='No', max_length=20, choices=YES_NO)
    studio_controled_temperature = models.CharField("Studio has 24/7 365 temperature control?", default='Yes', max_length=20, choices=YES_NO) 
    studio_dry_wipe_tops_of_crates = models.CharField(choices=FREQUENCY, max_length=100, default='Before Use')
    studio_dry_wiped = models.CharField(choices=FREQUENCY, max_length=100, default='Once a week')
    studio_smoking = models.CharField("Smoking is allowed in the studio?", default='No', max_length=20, choices=YES_NO)
    studio_gloves =  models.CharField("Cotton Gloves are required when handeling records?", default='No', max_length=20, choices=YES_NO)
    studio_thoroughfare = models.CharField("Studio is located in a thoroughfare?", default='No', max_length=20, choices=YES_NO)
    studio_turntables_dusted_and_vacummed = models.CharField(choices=FREQUENCY, max_length=100, default='Before Use')
    studio_vacuumed = models.CharField(choices=FREQUENCY, max_length=100, default='Once a week')
    studio_vestibule = models.CharField("Studio has a dust control vestibule?", default='No', max_length=20, choices=YES_NO)
    studio_wet_wiped = models.CharField(choices=FREQUENCY, max_length=100, default='Fortnightly')
    #endregion

    def __str__(self):
        return str(self.name)
    class Meta:
        ordering = ['name']

class Address(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    include_first_and_last_names = models.BooleanField(default=True)
    c_o = models.CharField(max_length=100, blank=True)
    unit_number = models.CharField(max_length=10, blank=True)
    street_number = models.CharField(max_length=10, blank=True)
    street_name = models.CharField(max_length=100, blank=True)
    suburb = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=100, blank=True)
    island = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' : ' + self.city + ' ' + self.country



class VinylDistributor(models.Model):
    name = models.CharField(max_length=200)
    distributor_code = models.CharField(max_length=3)
    country = models.CharField(max_length=100)
    currency = models.CharField(max_length=50)
    discount = models.DecimalField(decimal_places=2, max_digits=4, blank=True, null=True)
    weight_already_in_transit = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    auto_update = models.BooleanField(default=False)

    @property
    def currency_symbol(self):
        if self.currency == 'EUR':
            return "€"
        elif self.currency == 'GBP':
            return "£"
        else:
            return "$"
        
    def __str__(self):
        return self.name

class VinylShipping(models.Model):
    locations = models.CharField(max_length=100)
    shipping_cost_destination_currency = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.locations


    

#region choices

class Country(models.Model):
    country = models.CharField(max_length=200)
    def __str__(self):
        return self.country
    class Meta:
        ordering = ['country']

class Currency(models.Model):
    currency = models.CharField(max_length=100)
    exchange_rate = models.DecimalField(decimal_places=2, max_digits=10)
    def __str__(self):
        return self.currency
    class Meta:
        ordering = ['currency']
        
class VinylColour(models.Model):
    color = models.CharField(max_length=200)
    def __str__(self):
        return self.color
    class Meta:
        ordering = ['color']

class VinylPlateSize(models.Model):
    plate_size = models.CharField(max_length=200)
    def __str__(self):
        return self.plate_size

class VinylSleeveType(models.Model):
    sleeve = models.CharField(max_length=200)
    def __str__(self):
        return self.sleeve
    class Meta:
        ordering = ['sleeve']

class VinylReleaseType(models.Model):
    release_type = models.CharField(max_length=200)
    def __str__(self):
        return self.release_type
    class Meta:
        ordering = ['release_type']

class VinylCondition(models.Model):
    condition = models.CharField(max_length=200)
    name = models.CharField(max_length=200, default='')
    def __str__(self):
        return str(self.name) + ' (' + str(self.condition) + ')'

class CrateType(models.Model):
    variation = models.CharField(max_length=200)
    def __str__(self):
        return self.variation
    class Meta:
        ordering = ['variation']

class VinylIndex(models.Model):
    index = models.CharField(max_length=200)
    def __str__(self):
        return self.index
    class Meta:
        ordering = ['index']

class GenreOld(models.Model):
    genre = models.CharField(max_length=200)
    def __str__(self):
        return self.genre
    class Meta:
        ordering = ['genre']

class Vibe(models.Model):
    vibe = models.CharField(max_length=200)
    def __str__(self):
        return self.vibe
    class Meta:
        ordering = ['vibe']

class EnergyLevel(models.Model):
    energy_level = models.CharField(max_length=200)
    def __str__(self):
        return self.energy_level
    class Meta:
        ordering = ['energy_level']
#endregion

#region member incl. library as member
class LibraryShopBlockedLabels(models.Model):
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='library_shop_blocked_labels_member', limit_choices_to={'is_library_shop': True})
    label_name = models.CharField(max_length=200, null=True)

    class Meta:
        ordering = ['label_name',]

    def __str__(self):
        return str(self.label_name)
    
class Member(models.Model):
    #region basic info
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member')
    address = models.OneToOneField(Address, on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    membership_number = models.CharField(max_length=6, default='')
    account_credit = models.DecimalField(decimal_places=2, max_digits=10, default=Decimal('0.00'))
    active = models.BooleanField(default=True)
    #endregion

    #region library
    library = models.ForeignKey(Library, on_delete=models.PROTECT, blank=True, null=True)
    is_library_shop = models.BooleanField(default=False)
    @property
    def blocked_labels(self):
        bls = LibraryShopBlockedLabels.objects.filter(member=self)
        return bls
    #endregion

    #region professional services
    is_professional_service_provider = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    #endregion

    @property
    def order_request_items(self):
        from accounts.models import OrderRequestItem
        members_order_request_items = OrderRequestItem.objects.filter(
            order_request__member=self)
        return members_order_request_items
    
    @property
    def ordered_items(self):
        sp = self.order_request_items.filter(
            stockpiled=False).order_by(
            'vinyl_release__catalog_number')
        return sp
    
    @property
    def stockpile(self):
        sp = self.order_request_items.filter(
            stockpiled=True).filter(
            en_route=False).filter(
            delivered=False).order_by(
            'vinyl_release__catalog_number')
        return sp
    

    
    class Meta:
        ordering = ['membership_number']

    def __str__(self):
        return self.membership_number + ' : ' + self.user.first_name + ' ' + self.user.last_name
#endregion

#region auto add a member instance when adding a user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Member.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.member.save()
#endregion