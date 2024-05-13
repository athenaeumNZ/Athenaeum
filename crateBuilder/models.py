from django.db import models
from choices.models import Genre
from management.models import EnergyLevel, Vibe, Member

class CrateGrandParent(models.Model):
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, null=True, blank=True, related_name='parent_crate_genre')
    vibe = models.ForeignKey(Vibe, on_delete=models.PROTECT, null=True, blank=True, related_name='parent_crate_vibe')
    energy_level = models.ForeignKey(EnergyLevel, on_delete=models.PROTECT, null=True, blank=True, related_name='parent_crate_energy_level')

    @property
    def crate_grand_parent_identifier(self):
        cgp_id = str(self.genre) + ' ' + str(self.vibe)[slice(1)] + str(self.energy_level)

        return cgp_id

    @property
    def crate_id(self):
        c_id = self.crate_grand_parent_identifier
        return c_id
       
    class Meta:
        ordering = ['genre', 'vibe', 'energy_level']

    def __str__(self):
        return self.crate_grand_parent_identifier


class CrateParent(models.Model):
    crate_grand_parent = models.ForeignKey(CrateGrandParent, on_delete=models.PROTECT, blank=True, null=True, related_name='crate_grand_parent_crate_parent')
    member = models.ForeignKey(Member, on_delete=models.PROTECT, blank=True, null=True, related_name='crate_parent_member')
    date_created = models.DateField(auto_now_add=True, blank=True)
    date_modified = models.DateField(auto_now=True)

    @property
    def crate_parent_identifier(self):
        if self.member != None:
            cp_id = str(self.member.membership_number) + ' ' + str(self.crate_grand_parent)
        else:
            cp_id = ''
        return cp_id
    
    @property
    def crate_id(self):
        if self.crate_grand_parent != None:
            cid = self.crate_grand_parent.crate_id
        else:
            cid = ''
        return cid
    
    @property
    def crate_children(self):
        cc = CrateChild.objects.filter(crate_parent=self)
        return cc
    
    class Meta:
        ordering = ['member', 'crate_grand_parent',]

    def __str__(self):
        return self.crate_parent_identifier


class CrateChild(models.Model):
    crate_parent = models.ForeignKey(CrateParent, on_delete=models.PROTECT, blank=True, null=True, related_name='crate_crate_parent')
    index_start = models.CharField(max_length=1, default = '0')
    index_end = models.CharField(max_length=1, default = 'Z')

    @property
    def crate_child_identifier(self):
        if self.crate_parent != None:
            cc_id = str(self.crate_parent.crate_parent_identifier) + ' ' + str(self.index_start) + '-' + str(self.index_end)
        else:
            cc_id = ''
        return cc_id
    
    @property
    def crate_id(self):
        if self.crate_parent != None:
            cid = self.crate_parent.crate_id
        else:
            cid = ''
        return cid
    
    class Meta:
        ordering = ['crate_parent', 'index_start']

    def __str__(self):
        return self.crate_child_identifier
