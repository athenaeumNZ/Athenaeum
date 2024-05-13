from management.models import Member, Library
from members.models import MemberPlate
from musicDatabase.models import VinylPlate, VinylRelease
from vinylShop.models import StockItem


def member_recommendations_based_on_member_releases(member_id, library_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    member_plates = MemberPlate.objects.filter(member=member)
    member_plate_crate_ids = MemberPlate.objects.filter(member=member).values_list('vinyl_plate__related_vinyl_track__crate_id', flat=True).filter(vinyl_plate__related_vinyl_track__crate_id__isnull=False)
    member_plates_vinyl_plate_ids = member_plates.distinct().values_list('vinyl_plate__id', flat=True)
    member_plates_vinyl_plates_release_ids = VinylPlate.objects.filter(id__in=member_plates_vinyl_plate_ids).distinct().values_list('related_release__id', flat=True)
    member_vinyl_releases = VinylRelease.objects.filter(id__in=member_plates_vinyl_plates_release_ids)
    stock_items = StockItem.objects.filter(library=library, quantity_plus_quantity_incoming_stock__gte=1).exclude(vinyl_release__in=member_vinyl_releases)
    final_stock_items = []
    for i in stock_items:
        for j in i.vinyl_release.crate_id:
            if j in member_plate_crate_ids:
                if i not in final_stock_items:
                    final_stock_items.append(i)
    return final_stock_items