from django.db import models


class CrateType(models.Model):
    crate_type = models.CharField(max_length=200)
    def __str__(self):
        return self.crate_type
    class Meta:
        ordering = ['crate_type']

class Gender(models.Model):
    gender = models.CharField(max_length=200)
    def __str__(self):
        return self.gender
    class Meta:
        ordering = ['gender']

class CountryNew(models.Model):
    country = models.CharField(max_length=200)
    def __str__(self):
        return self.country
    class Meta:
        ordering = ['country']

class CurrencyNew(models.Model):
    currency = models.CharField(max_length=100)
    exchange_rate = models.DecimalField(decimal_places=2, max_digits=10)
    def __str__(self):
        return self.currency
    class Meta:
        ordering = ['currency']
        
class VinylColourNew(models.Model):
    color = models.CharField(max_length=200)
    def __str__(self):
        return self.color
    class Meta:
        ordering = ['color']

class VinylPlateSizeNew(models.Model):
    plate_size = models.CharField(max_length=200)
    def __str__(self):
        return self.plate_size

class VinylSleeveTypeNew(models.Model):
    sleeve = models.CharField(max_length=200)
    def __str__(self):
        return self.sleeve
    class Meta:
        ordering = ['sleeve']

class VinylReleaseTypeNew(models.Model):
    release_type = models.CharField(max_length=200)
    def __str__(self):
        return self.release_type
    class Meta:
        ordering = ['release_type']

class VinylConditionNew(models.Model):
    condition = models.CharField(max_length=200)
    name = models.CharField(max_length=200, default='')
    def __str__(self):
        return str(self.name) + ' (' + str(self.condition) + ')'

class VinylIndexNew(models.Model):
    index = models.CharField(max_length=200)
    def __str__(self):
        return self.index
    class Meta:
        ordering = ['index']

class Genre(models.Model):
    genre = models.CharField(max_length=200)
    def __str__(self):
        return self.genre
    class Meta:
        ordering = ['genre']

class VibeNew(models.Model):
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