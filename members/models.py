from django.db import models
from accounts.models import OrderRequestItem
from crateBuilder.models import CrateParent

from management.models import Member, VinylColour, VinylCondition, VinylSleeveType
from musicDatabase.models import VinylPlate, VinylRelease, VinylTrack
    
class MemberReleaseStatusChoices(models.Model):
    status = models.CharField(max_length=100)
    def __str__(self):
        return str(self.status)
    
class MemberRelease(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='member_release_member')
    vinyl_release = models.ForeignKey(VinylRelease, on_delete=models.PROTECT, related_name='member_release_vinyl_release')
    status = models.ForeignKey(MemberReleaseStatusChoices, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_release_status')
    order_request_item = models.ForeignKey(OrderRequestItem, on_delete=models.SET_NULL, related_name='member_release_order_request_item', null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.member) + ' ' + str(self.vinyl_release)

class MemberPlate(models.Model):
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='member_plate_member')
    member_release = models.ForeignKey(MemberRelease, on_delete=models.PROTECT, related_name='member_plate_member_release')
    crate_parent = models.ForeignKey(CrateParent, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_plate_crate_parent')
    desired_crate_parent_option_crate_parent = models.ForeignKey(CrateParent, on_delete=models.SET_NULL, null=True, blank=True, related_name='member_plate_desired_crate_parent_option_crate_parent')
    crate_parent_desired_option = models.BooleanField(default=False)
    vinyl_plate = models.ForeignKey(VinylPlate, on_delete=models.PROTECT, related_name='member_plate_vinyl_plate')
    vinyl_condition = models.ForeignKey(VinylCondition, on_delete=models.SET_NULL, null=True, blank=True)
    vinyl_colour = models.ForeignKey(VinylColour, on_delete=models.SET_NULL, null=True, blank=True)
    plate_sleeve_type =  models.ForeignKey(VinylSleeveType, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def crate_ids(self):
        crate_ids = []
        vinyl_tracks = VinylTrack.objects.filter(related_vinyl_plate=self.vinyl_plate)
        for i in vinyl_tracks:
            crate_ids.append(i.crate_id)
        return crate_ids

    def __str__(self):
        return str(self.member_release) + ' ' + str(self.vinyl_plate)