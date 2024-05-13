from django.shortcuts import render
from django.urls import resolve
import numpy as np
from accounts.models import OrderRequestItem
from crateBuilder.models import CrateChild, CrateGrandParent, CrateParent
from choices.models import Genre
from management.models import EnergyLevel, Member, Library, Vibe
from members.models import MemberPlate, MemberRelease, MemberReleaseStatusChoices
from musicDatabase.models import VinylPlate, VinylRelease, VinylTrack
from shoppingCart.shopping_cart import ShoppingCart
from vinylShop.models import StockItem

def form_search_variables(request, context):
    if 'search_artist' in request.POST:
        context['search_artist'] = request.POST['search_artist']
    if 'search_catalog' in request.POST:
        context['search_catalog'] = request.POST['search_catalog']
    if 'search_label' in request.POST:
        context['search_label'] = request.POST['search_label']
    if 'search_title' in request.POST:
        context['search_title'] = request.POST['search_title']
    return context

def form_variables(request, context):
    if 'crate_id' in request.POST:
        context['crate_id'] = request.POST['crate_id']
    if 'crate_parent_id' in request.POST:
        context['crate_parent_id'] = request.POST['crate_parent_id']
    if 'display_searched_releases' in request.POST:
        context['display_searched_releases'] = request.POST['display_searched_releases']
    if 'display_stock' in request.POST:
        context['display_stock'] = request.POST['display_stock']
    if 'display_unallocated' in request.POST:
        context['display_unallocated'] = request.POST['display_unallocated']
    if 'has_been_triggered' in request.POST:
        context['has_been_triggered'] = 'has_been_triggered'
    if 'member_id' in request.POST:
        context['member_id'] = request.POST['member_id']
        if request.POST['member_id'] != '':
            context['member'] = Member.objects.get(id=request.POST['member_id'])
    if 'member_plate_id' in request.POST and request.POST['member_plate_id'] != '':
        context['member_plate_id'] = request.POST['member_plate_id']
        context['member_release'] = MemberPlate.objects.get(id=request.POST['member_plate_id'])
        context['member_release'] = context['member_release'].member_release
    if 'previous_url' in request.POST:
        context['previous_url'] = request.POST['previous_url']
    if 'previous_vertical_location' in request.POST:
        context['previous_vertical_location'] = request.POST['previous_vertical_location']
    if 'stock_item_id' in request.POST:
        context['stock_item_id'] = request.POST['stock_item_id']
        if context['stock_item_id'] != '':
            context['stock_item'] = StockItem.objects.get(id=request.POST['stock_item_id'])
    if 'vinyl_release_id' in request.POST:
        context['vinyl_release_id'] = request.POST['vinyl_release_id']
        context['vinyl_release'] = VinylRelease.objects.get(id=request.POST['vinyl_release_id'])
    return context

def return_location(context):
    if context['previous_url'] == 'plate_sorter':
        location = 'return_to_plate_sorter.html'
    elif context['previous_url'] == 'vinyl_release':
        location = 'return_to_vinyl_release.html'
    elif context['previous_url'] == 'shopping_cart':
        location = 'return_to_shopping_cart.html'
    else:
        location = 'return_to_member_dashboard.html'
    return location

def by_size(words,size):
    result = []
    for word in words:
        if len(word)>=size:
            result.append(word)
    return result
    

#endregion

def member_plate_crate_parent_set(request, library_id):
    library = Library.objects.get(id=library_id)
    plate = MemberPlate.objects.get(id=request.POST['member_plate_id'])
    desired_crate_parent_option_crate_parent = CrateParent.objects.get(id=request.POST['desired_crate_parent_option_crate_parent_id'])
    plate.crate_parent_desired_option = True
    plate.desired_crate_parent_option_crate_parent = desired_crate_parent_option_crate_parent
    plate.save()
    context = {
        'library': library,
    }
    form_variables(request, context)
    location = return_location(context)
    return render(request, location, context)

def member_release_create(request, library_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=request.POST['member_id'])
    vinyl_release = VinylRelease.objects.get(id=request.POST['vinyl_release_id'])
    in_collection = MemberReleaseStatusChoices.objects.get(status='In Collection')
    in_want_list = MemberReleaseStatusChoices.objects.get(status='In Want List')
    if len(MemberRelease.objects.filter(vinyl_release=vinyl_release, status=in_want_list)) >= 1:
    #region want_list_member_release
        want_list_member_release = MemberRelease.objects.get(
            member=member,
            vinyl_release=vinyl_release,
            status=in_want_list,
        )
        want_list_member_release.status = in_collection
        want_list_member_release.save()
        member_release = want_list_member_release
    #endregion
    else:
    #region new member release
        new_member_release = MemberRelease(
            member = member,
            vinyl_release = vinyl_release,
            status = in_collection,
        )
        new_member_release.save()
        member_release = new_member_release
        vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
        for k in vinyl_plates:
            new_member_plate = MemberPlate(
                member=member,
                member_release=new_member_release,
                vinyl_plate=k,
            )
            new_member_plate.save()
    #endregion
    if len(OrderRequestItem.objects.filter(member=member, vinyl_release = member_release.vinyl_release)) == 1:
    #region order request item
        order_request_item = OrderRequestItem.objects.get(
            member=member,
            vinyl_release = member_release.vinyl_release,
        )
        member_release.order_request_item = order_request_item
        member_release.save()
        if order_request_item.delivered == False:
            member_release.status = MemberReleaseStatusChoices.objects.get(status='In Coming')
            member_release.save()
    #endregion
    context = {
        'library': library,
        'member': member,
    }
    form_variables(request, context)
    location = return_location(context)
    return render(request, location, context)

def plate_move(request, library_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=request.POST['member_id'])
    plate = MemberPlate.objects.get(id=request.POST['member_plate_id'])
    if str(request.POST['crate_parent_id'])[:10] == 'create_new':
        new_crate_crate_id = str(request.POST['crate_parent_id'])[10:]
        genre = Genre.objects.get(genre=new_crate_crate_id[:-3])
        #region vibe
        if new_crate_crate_id[-2:-1] == 'G':
            vibe_name = 'Green'
        elif new_crate_crate_id[-2:-1] == 'B':
            vibe_name = 'Blue'
        elif new_crate_crate_id[-2:-1] == 'R':
            vibe_name = 'Red'
        else:
            vibe_name = 'Yellow'
        vibe = Vibe.objects.get(vibe=vibe_name)
        #endregion
        energy_level = EnergyLevel.objects.get(energy_level=new_crate_crate_id[-1:])
        #region crate grand parent
        if len(CrateGrandParent.objects.filter(genre=genre, vibe=vibe, energy_level=energy_level)) == 0:
            crate_grand_parent = CrateGrandParent(
                genre = genre,
                vibe = vibe,
                energy_level = energy_level,
            )
            crate_grand_parent.save()
        else:
            crate_grand_parent = CrateGrandParent.objects.get(genre=genre, vibe=vibe, energy_level=energy_level)
        #endregion
        #region crate parent
        if len(CrateParent.objects.filter(member=member, crate_grand_parent=crate_grand_parent)) == 0:
            crate_parent = CrateParent(
                member = member,
                crate_grand_parent = crate_grand_parent,   
            )
            crate_parent.save()
        else:
            crate_parent =  None
        plate.crate_parent = crate_parent
        plate.save()
        #endregion
        #region crate child
        crate_child = CrateChild(
            crate_parent = crate_parent,
            index_start = '0',
            index_end = 'Z'
        )
        crate_child.save()
        #endregion
    else:
        crate_parent = CrateParent.objects.get(id=request.POST['crate_parent_id'])
        plate.crate_parent = crate_parent
        plate.save()
    context = {
        'library': library,
    }
    form_variables(request, context)
    location = return_location(context)
    context['crate_parent_id'] = request.POST['crate_parent_actual_id']
    return render(request, location, context)

def plate_sorter(request, library_id):
    library = Library.objects.get(id=library_id)
    #region all
    member = Member.objects.get(id=request.POST['member_id'])
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    crate_id = request.POST['crate_id']
    #region CRATE PARENTS
    crate_parents = CrateParent.objects.filter(member=member)
    crate_parents_crate_ids = []
    for i in crate_parents:
        crate_parents_crate_ids.append(i.crate_id)
    #endregion
    #region CRATE PARENT
    if 'crate_parent_id' in request.POST and request.POST['crate_parent_id'] != '':
        crate_parent = CrateParent.objects.get(id=request.POST['crate_parent_id'])
    else:
        crate_parent = None
    #endregion
    #region MEMBER PLATES CRATE_ID's
    member_plates = MemberPlate.objects.filter(member=member)
    member_plate_crate_ids = MemberPlate.objects.filter(member=member).values_list('vinyl_plate__related_vinyl_track__crate_id', flat=True).filter(vinyl_plate__related_vinyl_track__crate_id__isnull=False)
    member_plate_crate_ids = by_size(member_plate_crate_ids,4)
    member_plate_crate_ids = sorted(member_plate_crate_ids, key=lambda x: x[0])
    member_plate_crate_ids = list(dict.fromkeys(member_plate_crate_ids))
    member_plates_by_crate_id = []
    for i in member_plate_crate_ids:
        this_crate_id_plates_count = len(member_plates.filter(vinyl_plate__related_vinyl_track__crate_id=i).distinct())
        member_plates_by_crate_id.append([i, this_crate_id_plates_count])
    member_plates_by_crate_id = sorted(member_plates_by_crate_id, key=lambda x: x[1], reverse=True)
    member_plates_by_crate_id.append(['Show All My Plates', len(member_plates)])
    #endregion
    #region VINYL PLATES in members collection PLATE_ID's
    member_plates = MemberPlate.objects.filter(member=member).order_by('member_release__vinyl_release__catalog_number').distinct()
    member_plates_vinyl_plate_ids = member_plates.values_list('vinyl_plate_id')
    member_plates_vinyl_plates = VinylPlate.objects.filter(id__in=member_plates_vinyl_plate_ids).distinct()
    #endregion     
    #region stock_item VINYL PLATES not in members collection
    stock_item_vinyl_release_ids = StockItem.objects.filter(library=library, unavailable=False).values_list('vinyl_release__id')
    stock_item_vinyl_plates_not_in_member_collection = VinylPlate.objects.filter(
        related_release__id__in=stock_item_vinyl_release_ids,
        related_vinyl_track__crate_id__in=member_plate_crate_ids).exclude(id__in=member_plates_vinyl_plate_ids).distinct()
    #endregion
    all_plates = []
    member_crate_member_plates_plates_ids = ''
    if 'crate_parent_id' in request.POST and request.POST['crate_parent_id'] != '':
    #region member_plates
        member_plates_in_crate = member_plates.filter(crate_parent=crate_parent)
        member_crate_member_plates_plates_ids = member_plates_in_crate.values_list('vinyl_plate__id').distinct()
        for i in member_plates_in_crate:
            member_plate = i
            vinyl_plate = member_plate.vinyl_plate
            vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
            #region stock item
            if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_plate.related_release)) >= 1:
                stock_item = StockItem.objects.get(
                    library = library,
                    vinyl_release = vinyl_plate.related_release
                )
            else:
                stock_item = None
            #endregion
            #region release title long
            if vinyl_plate.related_release != None:
                release_catalog_number_length = len(str(vinyl_plate.related_release.catalog_number))
                release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)
                release_title_long_length = len(release_title_long)
                adjusted_length = 60 - release_title_long_length - release_catalog_number_length
                if adjusted_length <= 0:
                    new_length = 60 - release_catalog_number_length
                    release_title_long = release_title_long[:new_length].strip('-').strip() + ' ...'
            else:
                release_title_long = ''
            #endregion
            #region plate crate ids
            vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
            vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
            vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
            vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
            #endregion
            all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
    #endregion
    
    if request.POST['display_unallocated'] == 'display_unallocated_plates':
    #region unallocated plates
        if crate_id == 'Show All My Plates':
            member_plates = member_plates.all()             
        else:
            member_plates = member_plates.filter(
                vinyl_plate__related_vinyl_track__crate_id=crate_id).exclude(
                    vinyl_plate__id__in=member_crate_member_plates_plates_ids).filter(vinyl_plate__related_vinyl_track__crate_id__isnull=False).distinct()
        for i in member_plates:
            member_plate = i
            vinyl_plate = member_plate.vinyl_plate
            vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
            #region stock item
            if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_plate.related_release)) >= 1:
                stock_item = StockItem.objects.get(
                    library = library,
                    vinyl_release = vinyl_plate.related_release
                )
            else:
                stock_item = None
            #endregion
            #region release title long
            if vinyl_plate.related_release != None:
                release_catalog_number_length = len(str(vinyl_plate.related_release.catalog_number))
                release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)
                release_title_long_length = len(release_title_long)
                adjusted_length = 60 - release_title_long_length - release_catalog_number_length
                if adjusted_length <= 0:
                    new_length = 60 - release_catalog_number_length
                    release_title_long = release_title_long[:new_length].strip('-').strip() + ' ...'
            else:
                release_title_long = ''
            #region plate crate ids
            vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
            vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
            vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
            vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
            #endregion
            all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
    #endregion
    
    stock_item_vinyl_plates_length = len(stock_item_vinyl_plates_not_in_member_collection.filter(related_vinyl_track__crate_id=crate_id))
    if 'display_stock' in request.POST and request.POST['display_stock'] == 'show_stock_plates':
    #region stock plates
        ''' update_availability
        stock_items = StockItem.objects.filter(library=library)
        for i in stock_items:
            shop_q = i.quantity_plus_quantity_incoming_stock
            dist_q = i.vinyl_release.stock_estimation
            dist_active = i.vinyl_release.distributor.active
            if shop_q >= 1:
                i.unavailable = False
                i.save()
            elif dist_active == True and dist_q != None and dist_q >= 1:
                i.unavailable = False
                i.save()
            else:
                i.unavailable = True
                i.save()
        '''
        stock_item_vinyl_plates = stock_item_vinyl_plates_not_in_member_collection.filter(related_vinyl_track__crate_id=crate_id)
        for i in stock_item_vinyl_plates:
            member_plate = None
            vinyl_plate = i
            vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
            #region stock item
            stock_item = stock_item = StockItem.objects.get(
                library = library,
                vinyl_release = vinyl_plate.related_release,
                )
            #endregion
            #region release title long
            if vinyl_plate.related_release != None:
                release_catalog_number_length = len(str(vinyl_plate.related_release.catalog_number))
                release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)
                release_title_long_length = len(release_title_long)
                adjusted_length = 60 - release_title_long_length - release_catalog_number_length
                if adjusted_length <= 0:
                    new_length = 60 - release_catalog_number_length
                    release_title_long = release_title_long[:new_length].strip('-').strip() + ' ...'
            else:
                release_title_long = ''
            #region plate crate ids
            vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
            vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
            vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
            vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
            #endregion
            all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
    #endregion
    
    if 'display_searched_releases' in request.POST and request.POST['display_searched_releases'] == 'display_searched_releases_plates':
    #region display_searched_releases
        vinyl_releases_full_length = len(VinylRelease.objects.all())
        vinyl_releases = VinylRelease.objects.all()
        #region filter releases
        if 'search_artist' in request.POST:
            vinyl_releases = vinyl_releases.filter(artist__contains=request.POST['search_artist'])
        if 'search_title' in request.POST:
            vinyl_releases = vinyl_releases.filter(release_title__contains=request.POST['search_title'])
        if 'search_label' in request.POST:
            vinyl_releases = vinyl_releases.filter(label__contains=request.POST['search_label'])
        if 'search_catalog' in request.POST:
            vinyl_releases = vinyl_releases.filter(catalog_number__contains=request.POST['search_catalog'])
        #endregion
        if len(vinyl_releases) != vinyl_releases_full_length:
            vinyl_releases = vinyl_releases[:100]
            #region vinyl_plates
            for i in vinyl_releases:
                vinyl_release = i
                vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
                for j in vinyl_plates:
                    #region member_plates
                    if len(MemberPlate.objects.filter(member=member, member_release__vinyl_release=j.related_release)) >= 1:
                        member_plate = MemberPlate.objects.get(
                            member = member,
                            vinyl_plate = j
                        )
                    else:
                        member_plate = None
                    vinyl_plate = j
                    vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
                    #region stock item
                    if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_plate.related_release)) >= 1:
                        stock_item = StockItem.objects.get(
                            library = library,
                            vinyl_release = vinyl_plate.related_release
                        )
                    else:
                        stock_item = None
                    #endregion
                    #region release title long
                    if vinyl_plate.related_release != None:
                        release_catalog_number_length = len(str(vinyl_plate.related_release.catalog_number))
                        release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)
                        release_title_long_length = len(release_title_long)
                        adjusted_length = 60 - release_title_long_length - release_catalog_number_length
                        if adjusted_length <= 0:
                            new_length = 60 - release_catalog_number_length
                            release_title_long = release_title_long[:new_length].strip('-').strip() + ' ...'
                    else:
                        release_title_long = ''
                    #region plate crate ids
                    vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
                    vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
                    vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
                    vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
                    #endregion
                    all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
            #endregion
            #endregion
    #endregion
    
    all_plates = sorted(all_plates, key=lambda x: x[0])

    #endregion
    #region MemberReleaseStatusChoices
    in_collection = MemberReleaseStatusChoices.objects.get(status='In Collection')
    in_coming = MemberReleaseStatusChoices.objects.get(status='In Coming')
    #endregion
    #endregion

    context = {
        'library': library,
        'member': member,
        'shopping_cart': shopping_cart,
        'items': items,
        'member_plate_crate_ids': member_plate_crate_ids,
        'crate_parents': crate_parents,
        'crate_parents_crate_ids': crate_parents_crate_ids,
        'crate_parent': crate_parent,
        'stock_item_vinyl_release_ids': stock_item_vinyl_release_ids,
        'stock_item_vinyl_plates_length': stock_item_vinyl_plates_length,
        'stock_item_vinyl_plates_not_in_member_collection': stock_item_vinyl_plates_not_in_member_collection,
        'member_plates': member_plates,
        'all_plates': all_plates,
        'member_plates_vinyl_plates': member_plates_vinyl_plates,
        'in_collection': in_collection,
        'in_coming': in_coming,
        'member_plates_by_crate_id': member_plates_by_crate_id,
    }
    context['previous_url'] = resolve(request.path_info).url_name
    form_variables(request, context)
    if 'search_artist' in request.POST:
        context['search_artist'] = request.POST['search_artist']
    if 'search_catalog' in request.POST:
        context['search_catalog'] = request.POST['search_catalog']
    if 'search_label' in request.POST:
        context['search_label'] = request.POST['search_label']
    if 'search_title' in request.POST:
        context['search_title'] = request.POST['search_title']
    return render(request,'plate_sorter.html', context)

def return_to_plate_sorter(request, library_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=request.POST['member_id'])
    context = {
        'library': library,
        'member': member,
    }
    form_variables(request, context)
    form_search_variables(request, context)
    return render(request, 'return_to_plate_sorter.html', context)

def stock_item_create_and_add_to_cart(request, library_id):
    library = Library.objects.get(id=library_id)
    vinyl_release = VinylRelease.objects.get(id=request.POST['vinyl_release_id'])
    if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_release)) == 0:
        new_stock_item = StockItem(
            library = library,
            vinyl_release = vinyl_release,
            quantity = 0,
            price = 999,
            added_by_member = True,
            updated_by_library_shop = False,
        )
        new_stock_item.save()
        stock_item = new_stock_item
        shopping_cart = ShoppingCart(request)
        shopping_cart.add(stock_item=stock_item)
    context = {
        'library': library,
    }
    form_variables(request, context)
    location = return_location(context)
    return render(request, location, context)






''' UNUSED
def plate_sorter_add_release_to_cart(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    stock_item = StockItem.objects.get(id=request.POST['stock_item_id'])
    shopping_cart = ShoppingCart(request)
    shopping_cart.add(stock_item=stock_item)
    page_vertical_location = request.POST['previous_vertical_location']
    member = Member.objects.get(id=member_id)
    context = {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'previous_vertical_location': page_vertical_location,
        'display_searched_releases': display_searched_releases,
    }
    return render(request, 'return_to_plate_sorter.html', context)

def plate_sorter_remove_release_from_cart(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    stock_item = StockItem.objects.get(id=request.POST['stock_item_id'])
    shopping_cart = ShoppingCart(request)
    shopping_cart.remove(stock_item=stock_item)
    page_vertical_location = request.POST['previous_vertical_location']
    member = Member.objects.get(id=member_id)
    context = {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'previous_vertical_location': page_vertical_location,
        'display_searched_releases': display_searched_releases,
    }
    return render(request, 'return_to_plate_sorter.html', context)

    
def plate_sorter(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    #region all
    if 'member_id' in request.POST:
        member = Member.objects.get(id=request.POST['member_id'])
    else:
        member = Member.objects.get(id=member_id)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    #region CRATE PARENTS
    crate_parents = CrateParent.objects.filter(member=member)
    crate_parents_crate_ids = []
    for i in crate_parents:
        crate_parents_crate_ids.append(i.crate_id)
    #endregion
    #region CRATE PARENT
    if crate_parent_id != 'None':
        crate_parent = CrateParent.objects.get(id=crate_parent_id)
    else:
        crate_parent = None
    #endregion
    #region MEMBER PLATES CRATE_ID's
    member_plates = MemberPlate.objects.filter(member=member)
    member_plate_crate_ids = MemberPlate.objects.filter(member=member).values_list('vinyl_plate__related_vinyl_track__crate_id', flat=True).filter(vinyl_plate__related_vinyl_track__crate_id__isnull=False)
    def by_size(words,size):
        result = []
        for word in words:
            if len(word)>=size:
                result.append(word)
        return result
    member_plate_crate_ids = by_size(member_plate_crate_ids,4)
    member_plate_crate_ids = sorted(member_plate_crate_ids, key=lambda x: x[0])
    member_plate_crate_ids = list(dict.fromkeys(member_plate_crate_ids))
    #endregion
    #region VINYL PLATES in members collection PLATE_ID's
    member_plates = MemberPlate.objects.filter(member=member).order_by('member_release__vinyl_release__catalog_number').distinct()
    member_plates_vinyl_plate_ids = member_plates.values_list('vinyl_plate_id')
    member_plates_vinyl_plates = VinylPlate.objects.filter(id__in=member_plates_vinyl_plate_ids).distinct()
    #endregion     
    #region stock_item VINYL PLATES not in members collection
    stock_item_vinyl_release_ids = StockItem.objects.filter(library=library, unavailable=False).values_list('vinyl_release__id')
    stock_item_vinyl_plates_not_in_member_collection = VinylPlate.objects.filter(
        related_release__id__in=stock_item_vinyl_release_ids,
        related_vinyl_track__crate_id__in=member_plate_crate_ids).exclude(id__in=member_plates_vinyl_plate_ids).distinct()
    #endregion
    all_plates = []
    member_crate_member_plates_plates_ids = ''
    if crate_parent_id != 'None':
    #region member_plates
        member_plates_in_crate = member_plates.filter(crate_parent=crate_parent)
        member_crate_member_plates_plates_ids = member_plates_in_crate.values_list('vinyl_plate__id').distinct()
        for i in member_plates_in_crate:
            member_plate = i
            vinyl_plate = member_plate.vinyl_plate
            vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
            #region stock item
            if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_plate.related_release)) >= 1:
                stock_item = StockItem.objects.get(
                    library = library,
                    vinyl_release = vinyl_plate.related_release
                )
            else:
                stock_item = None
            #endregion
            #region release title long
            if vinyl_plate.related_release != None:
                release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)
                if len(release_title_long) >= 50:
                    release_title_long = release_title_long[:50].strip('-').strip() + ' ...'
            else:
                release_title_long = ''
            #endregion
            #region plate crate ids
            vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
            vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
            vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
            vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
            #endregion
            all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
    #endregion
    
    if display_unallocated == 'display_unallocated_plates':
    #region unallocated plates
        member_plates = member_plates.filter(
            vinyl_plate__related_vinyl_track__crate_id=crate_id).exclude(
                vinyl_plate__id__in=member_crate_member_plates_plates_ids).filter(vinyl_plate__related_vinyl_track__crate_id__isnull=False).distinct()
        for i in member_plates:
            member_plate = i
            vinyl_plate = member_plate.vinyl_plate
            vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
            #region stock item
            if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_plate.related_release)) >= 1:
                stock_item = StockItem.objects.get(
                    library = library,
                    vinyl_release = vinyl_plate.related_release
                )
            else:
                stock_item = None
            #endregion
            #region release title long
            if vinyl_plate.related_release != None:
                release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)
                if len(release_title_long) >= 50:
                    release_title_long = release_title_long[:50].strip('-').strip() + ' ...'
            else:
                release_title_long = ''
            #endregion
            #region plate crate ids
            vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
            vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
            vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
            vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
            #endregion
            all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
    #endregion
    
    if display_stock == 'show_stock_plates':
    #region stock plates
        
        stock_item_vinyl_plates = stock_item_vinyl_plates_not_in_member_collection.filter(related_vinyl_track__crate_id=crate_id)
        for i in stock_item_vinyl_plates:
            member_plate = None
            vinyl_plate = i
            vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
            #region stock item
            stock_item = stock_item = StockItem.objects.get(
                library = library,
                vinyl_release = vinyl_plate.related_release,
                )
            #endregion
            #region release title long
            if vinyl_plate.related_release != None:
                release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)  + ' - '
                if len(release_title_long) >= 50:
                    release_title_long = release_title_long[:50].strip('-').strip() + ' ...' 
            else:
                release_title_long = ''
            #endregion
            #region plate crate ids
            vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
            vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
            vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
            vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
            #endregion
            all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
    #endregion
    
    if display_searched_releases == 'display_searched_releases_plates':
    #region display_searched_releases
        vinyl_releases = VinylRelease.objects.all()
        #region filter releases
        if 'search_artist' in request.POST:
            vinyl_releases = vinyl_releases.filter(artist__contains=request.POST['search_artist'])
        if 'search_title' in request.POST:
            vinyl_releases = vinyl_releases.filter(release_title__contains=request.POST['search_title'])
        if 'search_label' in request.POST:
            vinyl_releases = vinyl_releases.filter(label__contains=request.POST['search_label'])
        if 'search_catalog' in request.POST:
            vinyl_releases = vinyl_releases.filter(catalog_number__contains=request.POST['search_catalog'])
        #endregion
        #region vinyl_plates
        vinyl_releases = vinyl_releases[:100]
        for i in vinyl_releases:
            vinyl_release = i
            vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
            for j in vinyl_plates:
                #region member_plates
                if len(MemberPlate.objects.filter(member=member, member_release__vinyl_release=j.related_release)) >= 1:
                    member_plate = MemberPlate.objects.get(
                        member = member,
                        vinyl_plate = j
                    )
                else:
                    member_plate = None
                vinyl_plate = j
                vinyl_plate_identifier = str(vinyl_plate.related_release) + str(vinyl_plate.plate_index)
                #region stock item
                if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_plate.related_release)) >= 1:
                    stock_item = StockItem.objects.get(
                        library = library,
                        vinyl_release = vinyl_plate.related_release
                    )
                else:
                    stock_item = None
                #endregion
                #region release title long
                if vinyl_plate.related_release != None:
                    release_title_long = str(vinyl_plate.related_release.artist) + ' - ' + str(vinyl_plate.related_release.release_title) + ' - ' + str(vinyl_plate.related_release.label)
                    if len(release_title_long) >= 50:
                        release_title_long = release_title_long[:50].strip('-').strip() + ' ...'
                else:
                    release_title_long = ''
                #endregion
                #region plate crate ids
                vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
                vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
                vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
                vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
                #endregion
                all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
        #endregion
    #endregion
    #endregion
    
    all_plates = sorted(all_plates, key=lambda x: x[0])
    #region previous_vertical_location
    if request.POST['previous_vertical_location']:
        previous_vertical_location = request.POST['previous_vertical_location']
    else:
        previous_vertical_location = 0
    #endregion
    #region MemberReleaseStatusChoices
    in_collection = MemberReleaseStatusChoices.objects.get(status='In Collection')
    in_coming = MemberReleaseStatusChoices.objects.get(status='In Coming')
    #endregion
    current_url = resolve(request.path_info).url_name
    #endregion
    context = {
        'library': library,
        'member': member,
        'shopping_cart': shopping_cart,
        'items': items,
        'member_plate_crate_ids': member_plate_crate_ids,
        'crate_parent_id': crate_parent_id,
        'crate_parents': crate_parents,
        'crate_parents_crate_ids': crate_parents_crate_ids,
        'crate_parent': crate_parent,
        'stock_item_vinyl_release_ids': stock_item_vinyl_release_ids,
        'stock_item_vinyl_plates_not_in_member_collection': stock_item_vinyl_plates_not_in_member_collection,
        'member_plates': member_plates,
        'crate_id': crate_id,
        
        'all_plates': all_plates,
        'member_plates_vinyl_plates': member_plates_vinyl_plates,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'display_searched_releases': display_searched_releases,
        'previous_vertical_location': previous_vertical_location,
        'in_collection': in_collection,
        'in_coming': in_coming,
        'previous_url': current_url,
    }
    if 'search_catalog' in request.POST:
        context['search_catalog'] = request.POST['search_catalog']
    if 'has_been_triggered' in request.POST:
        context['has_been_triggered'] = 'has_been_triggered'
        
    
    return render(request,'plate_sorter.html', context)

    '''

def stock_item_member_add_and_return_to_plate_sorter_submission(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    vinyl_release = VinylRelease.objects.get(catalog_number=request.POST['search_catalog'])
    member = Member.objects.get(id=member_id)
    if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_release)) == 0:
        new_stock_item = StockItem(
            library = library,
            vinyl_release = vinyl_release,
            quantity = 0,
            price = 999,
            added_by_member = True,
            updated_by_library_shop = False,
        )
        new_stock_item.save()
        stock_item = new_stock_item
        shopping_cart = ShoppingCart(request)
        shopping_cart.add(stock_item=stock_item)
    previous_vertical_location = request.POST['previous_vertical_location']
    context = {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'display_searched_releases': display_searched_releases, 
        'previous_vertical_location': previous_vertical_location,
        'search_catalog': request.POST['search_catalog'],
    }
    return render(request, 'return_to_plate_sorter.html', context) 
  
''' plate_sorter v1
def plate_sorter(request, library_id, member_id, crate_id, crate_parent_id, show_stock):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    if crate_parent_id != 'None':
        crate_parent = CrateParent.objects.get(id=crate_parent_id)
    else:
        crate_parent = None
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    current_url = resolve(request.path_info).url_name
    #region member_plates_crate_ids
    member_plate_crate_ids = MemberPlate.objects.filter(member=member).values_list('vinyl_plate__related_vinyl_track__crate_id', flat=True).filter(vinyl_plate__related_vinyl_track__crate_id__isnull=False)
    member_plate_crate_ids = member_plate_crate_ids
    member_plate_crate_ids = sorted(member_plate_crate_ids, key=lambda x: x[0])
    member_plate_crate_ids = list(dict.fromkeys(member_plate_crate_ids))
    #endregion 
    #region vinyl plates in members collection
    member_plates = MemberPlate.objects.filter(member=member, vinyl_plate__related_vinyl_track__crate_id=crate_id).order_by('member_release__vinyl_release__catalog_number').distinct()
    member_plates_vinyl_plate_ids = member_plates.values_list('vinyl_plate__id')
    member_plates_vinyl_plates = VinylPlate.objects.filter(id__in=member_plates_vinyl_plate_ids).distinct()
    #endregion  
    #region vinyl plates that have stock items * not in members collection
    stock_item_vinyl_release_ids = StockItem.objects.filter(library=library, quantity__gte=1).values_list('vinyl_release__id')
    stock_item_vinyl_plates = VinylPlate.objects.filter(
        related_release__id__in=stock_item_vinyl_release_ids,
        related_vinyl_track__crate_id=crate_id).exclude(id__in=member_plates_vinyl_plate_ids).distinct()
    stock_item_vinyl_plates_not_in_collection = stock_item_vinyl_plates.exclude(id__in=member_plates_vinyl_plate_ids)
    #endregion
    all_plates = []
    #region show stock items
    if show_stock == 'show_stock':
        for i in stock_item_vinyl_plates_not_in_collection:
            stock_item = StockItem.objects.filter(
                vinyl_release=i.related_release,
                library=library
                ).first()
            plate_identifier = str(i.related_release) + str(i.plate_index)
            all_plates.append([plate_identifier, i, None, stock_item])
    #endregion
    if crate_parent != None:
        member_plates_plate_ids = MemberPlate.objects.filter(member=member, crate_parent=crate_parent).order_by('member_release__vinyl_release__catalog_number').distinct().values_list('vinyl_plate__id')
        member_plates_vinyl_plates = VinylPlate.objects.filter(id__in=member_plates_plate_ids).distinct()
    for i in member_plates_vinyl_plates:
        member_plate = MemberPlate.objects.filter(
            vinyl_plate=i, ).first()
        plate_identifier = str(i.related_release) + str(i.plate_index)
        all_plates.append([plate_identifier, i, member_plate, None])
    
    all_plates = sorted(all_plates, key=lambda x: x[0])

    #region crates parents
    crate_parent_does_not_exist = False
    crate_parents = CrateParent.objects.filter(member=member)
    if crate_parent_id != 'None':
        crate_parent = CrateParent.objects.get(id=crate_parent_id)
        crate_id = str(crate_parent.crate_id)
    elif crate_id != 'None':
        genre = Genrejects.get(genre=str(crate_id)[:-3])
        if crate_id[-2:-1] == 'G':
            vibe_name = 'Green'
        elif crate_id[-2:-1] == 'B':
            vibe_name = 'Blue'
        elif crate_id[-2:-1] == 'R':
            vibe_name = 'Red'
        else:
            vibe_name = 'Yellow'
        vibe = Vibe.objects.get(vibe=vibe_name)
        energy_level = EnergyLevel.objects.get(energy_level=crate_id[-1:])
        if len(CrateGrandParent.objects.filter(genre=genre, vibe=vibe, energy_level=energy_level)) >= 1:
            crate_grand_parent = CrateGrandParent.objects.get(genre=genre, vibe=vibe, energy_level=energy_level)
            if len(CrateParent.objects.filter(member=member, crate_grand_parent=crate_grand_parent)) == 0:
                crate_parent_does_not_exist = True
            else:
                crate_parent_does_not_exist = False
        else:
            crate_parent_does_not_exist = True
    else:
        crate_parent_does_not_exist = False
    if crate_parent_id != 'None':
        crate_id = str(crate_id)[:-3]
    else:
        crate_id ='None'
    #endregion
    
    context = {
        'library': library,
        'member': member,
        'shopping_cart': shopping_cart,
        'items': items,
        'member_plates': member_plates,
        'crate_id': crate_id,
        'member_plate_crate_ids': member_plate_crate_ids,
        'stock_item_vinyl_plates': stock_item_vinyl_plates,
        'crate_parents': crate_parents,
        'member_plates_vinyl_plates': member_plates_vinyl_plates,
        'stock_item_vinyl_plates_not_in_collection': stock_item_vinyl_plates_not_in_collection,
        'all_plates': all_plates,
        'crate_parent_id': crate_parent_id,
        'show_stock': show_stock,
        'crate_parent': crate_parent,
        'crate_parent_does_not_exist': crate_parent_does_not_exist,
    }

    return render(request,'plate_sorter.html', context)
'''

def member_release_create_submission(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    vinyl_release = VinylRelease.objects.get(id=request.POST['vinyl_release_id'])
    in_collection = MemberReleaseStatusChoices.objects.get(status='In Collection')
    in_want_list = MemberReleaseStatusChoices.objects.get(status='In Want List')
    if len(MemberRelease.objects.filter(vinyl_release=vinyl_release, status=in_want_list)) >= 1:
        want_list_member_release = MemberRelease.objects.get(
            member=member_id,
            vinyl_release=vinyl_release,
            status=in_want_list,
        )
        want_list_member_release.status = in_collection
        want_list_member_release.save()
        member_release = want_list_member_release
    else:
        new_member_release = MemberRelease(
            member = member,
            vinyl_release = vinyl_release,
            status = in_collection,
        )
        new_member_release.save()
        member_release = new_member_release
        vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
        for k in vinyl_plates:
            new_member_plate = MemberPlate(
                member=member,
                member_release=new_member_release,
                vinyl_plate=k,
            )
            new_member_plate.save()
    if len(OrderRequestItem.objects.filter(
        member=member,
        vinyl_release = member_release.vinyl_release,
        )) == 1:
        order_request_item = OrderRequestItem.objects.get(
            member=member,
            vinyl_release = member_release.vinyl_release,
        )
        member_release.order_request_item = order_request_item
        member_release.save()
        if order_request_item.delivered == False:
            member_release.status = MemberReleaseStatusChoices.objects.get(status='In Coming')
            member_release.save()

    previous_vertical_location = request.POST['previous_vertical_location']
    if 'search_catalog' in request.POST:
        search_catalog = request.POST['search_catalog']
    else:
        search_catalog = None
    context = {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'previous_vertical_location': previous_vertical_location,
        'display_searched_releases': display_searched_releases,
        'search_catalog': search_catalog,
    }
    return render(request, 'return_to_plate_sorter.html', context )

def plate_move_submission(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    plate = MemberPlate.objects.get(id=request.POST['member_plate_id'])
    if str(request.POST['crate_parent_id'])[:10] == 'create_new':
        new_crate_crate_id = str(request.POST['crate_parent_id'])[10:]
        genre = Genrejects.get(genre=new_crate_crate_id[:-3])
        #region vibe
        if new_crate_crate_id[-2:-1] == 'G':
            vibe_name = 'Green'
        elif new_crate_crate_id[-2:-1] == 'B':
            vibe_name = 'Blue'
        elif new_crate_crate_id[-2:-1] == 'R':
            vibe_name = 'Red'
        else:
            vibe_name = 'Yellow'
        vibe = Vibe.objects.get(vibe=vibe_name)
        #endregion
        energy_level = EnergyLevel.objects.get(energy_level=new_crate_crate_id[-1:])
        #region crate grand parent
        if len(CrateGrandParent.objects.filter(genre=genre, vibe=vibe, energy_level=energy_level)) == 0:
            crate_grand_parent = CrateGrandParent(
                genre = genre,
                vibe = vibe,
                energy_level = energy_level,
            )
            crate_grand_parent.save()
        else:
            crate_grand_parent = CrateGrandParent.objects.get(genre=genre, vibe=vibe, energy_level=energy_level)
        #endregion
        #region crate parent
        if len(CrateParent.objects.filter(member=member, crate_grand_parent=crate_grand_parent)) == 0:
            crate_parent = CrateParent(
                member = member,
                crate_grand_parent = crate_grand_parent,   
            )
            crate_parent.save()
        else:
            crate_parent =  None
        plate.crate_parent = crate_parent
        plate.save()
        #endregion
        #region crate child
        crate_child = CrateChild(
            crate_parent = crate_parent,
            index_start = '0',
            index_end = 'Z'
        )
        crate_child.save()
        #endregion
    else:
        crate_parent = CrateParent.objects.get(id=request.POST['crate_parent_id'])
        plate.crate_parent = crate_parent
        plate.save()
    previous_vertical_location = request.POST['previous_vertical_location']

    context = {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'previous_vertical_location': previous_vertical_location,
        'display_searched_releases': display_searched_releases,
    }

    return render(request, 'return_to_plate_sorter.html', context)

def plate_crate_parent_desired_option_set_submission(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    plate = MemberPlate.objects.get(id=request.POST['member_plate_id'])
    desired_crate_parent_option_crate_parent = CrateParent.objects.get(id=request.POST['desired_crate_parent_option_crate_parent_id'])
    plate.crate_parent_desired_option = True
    plate.desired_crate_parent_option_crate_parent = desired_crate_parent_option_crate_parent
    plate.save()
    previous_vertical_location = request.POST['previous_vertical_location']

    context = {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'previous_vertical_location': previous_vertical_location,
        'display_searched_releases': display_searched_releases,
    }

    return render(request, 'return_to_plate_sorter.html', context)

def crate_parent_create_submission(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    genre = Genre.objects.get(genre=str(crate_id)[:-3])
    if crate_id[-2:-1] == 'G':
        vibe_name = 'Green'
    elif crate_id[-2:-1] == 'B':
        vibe_name = 'Blue'
    elif crate_id[-2:-1] == 'R':
        vibe_name = 'Red'
    else:
        vibe_name = 'Yellow'
    vibe = Vibe.objects.get(vibe=vibe_name)
    energy_level = EnergyLevel.objects.get(energy_level=crate_id[-1:])

    if len(CrateGrandParent.objects.filter(genre=genre, vibe=vibe, energy_level=energy_level)) == 0:
        crate_grand_parent = CrateGrandParent(
            genre = genre,
            vibe = vibe,
            energy_level = energy_level,
        )
        crate_grand_parent.save()
    else:
        crate_grand_parent = CrateGrandParent.objects.get(genre=genre, vibe=vibe, energy_level=energy_level)
    crate_grand_parent = crate_grand_parent
    if len(CrateParent.objects.filter(member=member, crate_grand_parent=crate_grand_parent)) == 0:
        crate_parent = CrateParent(
            member = member,
            crate_grand_parent = crate_grand_parent,   
        )
        crate_parent.save()
        crate_child = CrateChild(
            crate_parent = crate_parent,
            index_start = '0',
            index_end = 'Z'
        )
        crate_child.save()

    context = {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'previous_vertical_location': previous_vertical_location,
        'display_searched_releases': display_searched_releases,
    }

    return render(request, 'return_to_plate_sorter.html', context)

def form_variables_edited(request, context):
    if 'crate_id' in request.POST:
        context['crate_id'] = request.POST['crate_id']
    if 'crate_parent_id' in request.POST:
        context['crate_parent_id'] = request.POST['crate_parent_id']
    if 'display_searched_releases' in request.POST:
        context['display_searched_releases'] = request.POST['display_searched_releases']
    if 'display_stock' in request.POST:
        context['display_stock'] = request.POST['display_stock']
    if 'display_unallocated' in request.POST:
        context['display_unallocated'] = request.POST['display_unallocated']
    if 'has_been_triggered' in request.POST:
        context['has_been_triggered'] = 'has_been_triggered'
    if 'member_id' in request.POST and request.POST['member_id'] != '':
        context['member_id'] = request.POST['member_id']
        context['member'] = Member.objects.get(id=request.POST['member_id'])
    if 'member_plate_id' in request.POST and request.POST['member_plate_id'] != '':
        context['member_plate'] = MemberPlate.objects.get(id=request.POST['member_plate_id'])
    if 'member_release_id' in request.POST and request.POST['member_release_id'] != '':
        context['member_release'] = MemberRelease.objects.get(id=request.POST['member_release_id'])
    if 'previous_url' in request.POST:
        context['previous_url'] = request.POST['previous_url']
    if 'previous_vertical_location' in request.POST:
        context['previous_vertical_location'] = request.POST['previous_vertical_location']
    if 'release_id' in request.POST:
        context['release'] = VinylRelease.objects.get(id=request.POST['release_id'])
    if 'stock_item_id' in request.POST and request.POST['stock_item_id'] != '':
        context['stock_item'] = StockItem.objects.get(id=request.POST['stock_item_id'])
    if 'vinyl_release_id' in request.POST and request.POST['stock_item_id'] != '':
        context['vinyl_release'] = VinylRelease.objects.get(id=request.POST['vinyl_release_id'])
    return context


'''
def return_to_plate_sorter(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    previous_vertical_location = request.POST['previous_vertical_location']
    context = {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'previous_vertical_location': previous_vertical_location,
        'display_searched_releases': display_searched_releases,
    }
    context['search_catalog'] = request.POST['search_catalog']

    return render(request, 'return_to_plate_sorter.html', context)
'''
