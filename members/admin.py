from django.contrib import admin

from members.models import MemberReleaseStatusChoices, MemberRelease, MemberPlate


admin.site.register(MemberReleaseStatusChoices)

class MemberPlateInline(admin.TabularInline):
    model = MemberPlate
    search_fields = ['vinyl_plate']
    extra = 0

class MemberReleaseAdmin(admin.ModelAdmin):
    inlines = [MemberPlateInline]
    list_display = ['id', 'vinyl_release',]
    list_filter = ['vinyl_release', 'member__membership_number',]
    search_fields = ['vinyl_release__catalog_number', 'member__membership_number',]

admin.site.register(MemberRelease, MemberReleaseAdmin)

class MemberPlateAdmin(admin.ModelAdmin):
    search_fields = ['member_release__vinyl_release__catalog_number']

admin.site.register(MemberPlate, MemberPlateAdmin)