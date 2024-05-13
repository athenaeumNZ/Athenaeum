from datetime import date
from decimal import Decimal
from django.db import models
import librosa
from choices.models import Genre
from management.models import Currency, Member, VinylDistributor, VinylShipping

class ArtistWrittenAs(models.Model):
    real_name = models.CharField(max_length=200)
    use_this_artist_name = models.CharField(max_length=200)
    aliases = models.TextField(max_length=1000)

    def __str__(self):
        return str(self.use_this_artist_name) + ' - ' + str(self.real_name)
    
    class Meta:
        ordering = ['use_this_artist_name']

class VinylRelease(models.Model):
    YES_NO = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )

    catalog_number = models.CharField(max_length=50, unique=True)
    artist = models.CharField(max_length=100, null=True)
    release_title = models.CharField(max_length=100)
    label = models.CharField(max_length=70, blank=True, null=True)

    release_date = models.DateField(blank=True, null=True) # default to jan 01 of year if specifics are not availible.
    release_date_tbc = models.BooleanField(default=False)
    release_date_confirmed = models.CharField(choices=YES_NO, max_length=50, blank=True)

    country = models.CharField(default='UK', max_length=20, blank=True, null=True)
    
    plate_size = models.CharField(max_length=20, default='12"')
    sleeve_type = models.CharField(max_length=100, blank=True, null=True)
    release_type = models.CharField(max_length=100, blank=True, null=True)
    vinyl_colour = models.CharField(max_length=100, blank=True, null=True)
    plate_count = models.PositiveIntegerField(default=1)
    plate_count = models.PositiveIntegerField(default=1)
    average_tracks_per_side = models.CharField(blank=True, null=True, max_length=20)
    average_tracks_per_side_is_above_2 = models.BooleanField(blank=True,null=True)
    not_black = models.BooleanField(null=True, blank=True)

    master_genre = models.ForeignKey(Genre, on_delete=models.PROTECT, blank=True, null=True)
    is_repress = models.BooleanField(default=False)
    check_stock_availibility = models.BooleanField(default=False)
    artwork = models.ImageField(upload_to='static/musicDatabase/releaseArtwork', null=True, blank=True) # need to make two versions -> 30x30 & 200x200??
    artwork_small = models.ImageField(upload_to='static/musicDatabase/releaseArtworkSmall', null=True, blank=True)
    # sale terms
    distributor = models.ForeignKey(VinylDistributor, on_delete=models.PROTECT)

    #region stock
    stock_estimation = models.PositiveIntegerField(blank=True, null=True)
    @property
    def stock(self):
        distributor = VinylDistributor.objects.get(name=self.distributor)
        if distributor.active == False:
            return 0
        else:
            return self.stock_estimation
    #endregion
    
    cost_price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)

    on_previous_weekly_release_sheet = models.BooleanField(default=False)
    back_in_stock = models.BooleanField(default=False)
    
    date_added = models.DateField(auto_now_add=True)

    most_common = models.CharField(max_length=100, blank=True, null=True)
    
    @property
    def crate_id(self):
        vinyl_plates = VinylPlate.objects.filter(related_release=self)
        crate_ids = []
        for i in vinyl_plates:
            vinyl_tracks = VinylTrack.objects.filter(related_vinyl_plate=i)
            for j in vinyl_tracks:
                if j.crate_id_property not in crate_ids:
                    if j.crate_id_property != None:
                        if len(j.crate_id_property) >= 4 and str(j.crate_id_property)[0] != '-':
                            crate_ids.append(j.crate_id_property)
        if len(crate_ids) == 0:
            if self.master_genre_new == None:
                crate_ids.append('! UNCATERGORIZED !')
            else:
                crate_ids.append('* Release Genre * ' + str(self.master_genre_new))
        return crate_ids

    @property

    def cost_price_NZD(self):
        if self.distributor != None:
            currency_exchange = (Currency.objects.get(currency=str(self.distributor.currency) + ' to NZD')).exchange_rate
            discount = self.distributor.discount
        else:
            currency_exchange = 1
            discount = 0
        if self.distributor != None:
            price_nz = self.cost_price * currency_exchange * Decimal(1 - discount)
            return round(price_nz, 2)
    
    @property
    def pre_sale_price_NZ(self):
        if self.distributor != None:
            currency_exchange = (Currency.objects.get(currency=str(self.distributor.currency) + ' to NZD')).exchange_rate
            discount = self.distributor.discount
        else:
            currency_exchange = 1
            discount = 0
            
        number_of_plates = self.plate_count

        if self.distributor != None:
            if self.distributor.name == 'Southbound Distribution':
                price_nz = self.cost_price + Decimal(4) * number_of_plates
            else:
                price_nz = self.cost_price * currency_exchange * (1 - discount) + Decimal(4.5) * number_of_plates
        else:
            price_nz = 0

        return round(price_nz, 2)

    @property
    def recommended_sale_price_NZ(self):
        if self.plate_size == '7"':
            if self.distributor != 'Southbound Distribution':
                shipping = 2
            elif self.distributor == 'Kudos Distribution':
                shipping = 4
            else:
                shipping = 1
        elif self.plate_size == '10"':
            if self.distributor != 'Southbound Distribution':
                shipping = Decimal(4.5)
            elif self.distributor == 'Kudos Distribution':
                shipping = 7
            else:
                shipping = Decimal(1.5)
        else:
            if self.distributor != 'Southbound Distribution':
                shipping = Decimal(6)
            elif self.distributor == 'Kudos Distribution':
                shipping = 9
            else:
                shipping = 2

        rsp = (self.pre_sale_price_NZ + shipping * self.plate_count)

        return round(rsp, 2)
        
    @property
    def this_date(self):
        return date.today()
    
    @property
    def repress_request_count(self):
        vinyl_release_request_repress = VinylReleaseRepressRequest.objects.filter(vinyl_release=self)
        count = len(vinyl_release_request_repress)
        return count
    
    # tempoary feilds
    not_all_categorized = models.BooleanField(blank=True, default=False)

    @property
    def vinyl_plates(self):
        vps = VinylPlate.objects.filter(related_release=self)
        return vps
    
    def __str__(self):
        return str(self.catalog_number)
    

    class Meta:
        ordering = ['catalog_number']

class VinylReleaseRepressRequest(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="vinyl_release_repress_request_member")
    vinyl_release = models.ForeignKey(VinylRelease, on_delete=models.CASCADE, related_name="vinyl_release_repress_request_vinyl_release")
    added = models.DateField(auto_now_add=True)
    class Meta:
        ordering = ['vinyl_release', 'added']
    def __str__(self):
        return str(self.vinyl_release)

class VinylPlate(models.Model):
    related_release = models.ForeignKey(VinylRelease, on_delete=models.CASCADE, null=True, blank=True, related_name='related_vinyl_plate')
    plate_index = models.CharField(default='a/b', max_length=20)

    def __str__(self):
        return str(self.related_release) + ' ' + str(self.plate_index)
    
    class Meta:
            ordering = ['related_release', 'plate_index']

class VinylTrack(models.Model):
    YES_NO = (
        ('Yes', 'Yes'),
        ('No', 'No')
    )
    artist = models.CharField(max_length=100)
    remixer = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=128)
    related_vinyl_plate = models.ForeignKey(VinylPlate, on_delete=models.CASCADE, null=True, blank=True, related_name='related_vinyl_track')
    
    index = models.CharField(max_length=5)

    audio = models.FileField(upload_to='static/musicDatabase/trackAudioClips', blank=True, null=True)
    bpm = models.PositiveIntegerField(blank=True, null=True)  
    genre = models.CharField(max_length=50, blank=True, null=True, default='-')

    @property
    def release_master_genre(self):
        if self.related_vinyl_plate != None:
            vinyl_release = self.related_vinyl_plate.related_release
            if vinyl_release != None:
                if vinyl_release.master_genre_new != None:
                    master_genre = vinyl_release.master_genre_new
                    return master_genre
                else:
                    return None
            else:
                return None
        else:
            return None

    vibe = models.CharField(max_length=20, blank=True, null=True, default='-')
    energy_level = models.CharField(max_length=10, blank=True, null=True, default='-')
    crate_id = models.CharField(max_length=50, blank=True, null=True, default='-') # To Remove- we shouldn't need it now

    @property
    def crate_id_property(self):
        if self.genre != '-' and self.genre != '':
            genre = str(self.genre)
        else:
            genre = 'None'
        if self.vibe != '-' and self.vibe != '':
            vibe = str(self.vibe)
        else:
            vibe = 'None'
        if self.energy_level != '-' and self.energy_level != '':
            energy_level = str(self.energy_level)
        else:
            energy_level = 'None'
        if genre != 'None' and vibe != 'None' and energy_level != 'None':
            crate_id = str(genre) + ' ' + str(vibe[0]) + str(energy_level)
            if len(str(crate_id)) >= 4:
                crate_id = crate_id
            else:
                crate_id = None
        else:
            crate_id = None
        return crate_id
    
    def analyze_bpm(self):
        ''' Analyzes the BPM of the audio file associated with this VinylTrack instance. '''
        if self.audio:
            audio_path = self.audio.path
            try:
                # Load audio file
                y, sr = librosa.load(audio_path)
                
                # Calculate BPM
                start_bpm = 172
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=start_bpm)

                # Update instance's BPM field
                self.bpm = int(tempo)
                self.save()
                return f"BPM analysis completed for {self.title}"
            except Exception as e:
                # Handle any errors that may occur during the analysis
                return f"Error analyzing BPM for {self.title}: {e}"
        else:
            return "No audio file associated with this VinylTrack instance"
    
    catergorization_final = models.CharField(choices=YES_NO, max_length=50, blank=True, null=True, default='-')
    key_in = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.related_vinyl_plate) + ' ' + str(self.index)

    class Meta:
        ordering = ['related_vinyl_plate__related_release__catalog_number', 'index']
