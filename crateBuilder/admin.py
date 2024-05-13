from django.contrib import admin

from crateBuilder.models import CrateChild, CrateGrandParent, CrateParent

admin.site.register(CrateGrandParent)
admin.site.register(CrateParent)
admin.site.register(CrateChild)

