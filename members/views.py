import collections
from datetime import datetime, timedelta
from decimal import Decimal
from django.urls import resolve
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from accounts.admin import OrderRequestItemAdmin
from accounts.models import Invoice, OrderRequestItem

from cart.models import Order, OrderItem

from management.models import Address, Library, Member, Crate, VinylCondition
from members.models import MemberPlate, MemberRelease, MemberReleaseStatusChoices
from musicDatabase.models import VinylPlate, VinylRelease, VinylTrack
from professionalServices.models import ProfessionalServicesInvoice
from shoppingCart.shopping_cart import ShoppingCart
from vinylLibrary.models import LibraryCrate, LibraryPlate, SubCrate
import pandas as pd












def member_address_print_out(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member= Member.objects.get(id=member_id)
    context = {
        'library': library,
        'member': member,
    }
    return render(request, 'member_address_print_out.html', context)

def member_dashboard(request, library_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=request.POST['member_id'])
    order_request_items = OrderRequestItem.objects.filter(
        member = member,
        hidden_from_member = False,
        unavailable = False)
    #region order_request_items_stockpiled
    order_request_items_stockpiled = order_request_items.filter(
        stockpiled = True,
        invoiced = False,
        to_become_shop_stock = False
        )
    total_weight_of_stockpile = 0
    if len(order_request_items_stockpiled) >= 1:
        for s in order_request_items_stockpiled:
            total_weight_of_stockpile += s.weight_item
        total_weight_of_stockpile = (total_weight_of_stockpile * 25) + 200

        sub_total_of_stockpile = 0
        for s in order_request_items_stockpiled:
            if s.sale_price != None:
                sub_total_of_stockpile += s.sale_price
        
        gst_of_stockpile = round(sub_total_of_stockpile / 100 * 15, 2)
        total_of_stockpile_including_gst = round(Decimal(sub_total_of_stockpile) + Decimal(gst_of_stockpile), 2)
        address = Address.objects.get(member=member)

        if total_weight_of_stockpile <= 3000:
            if address.island == 'North':
                courier_price = 15 + 2
                economy_price = courier_price - 2
                signed_courier_price = courier_price + 3
            else:
                courier_price = 12 + 2
                economy_price = 0
                signed_courier_price = courier_price + 3

        elif total_weight_of_stockpile <= 10000:
            if address.island == 'North':
                courier_price = 74 + 2
                economy_price = 0
                signed_courier_price = courier_price + 3
            else:
                courier_price = 24 + 2
                economy_price = 0
                signed_courier_price = courier_price + 3
        else:
            courier_price = 0
            economy_price = 0
            signed_courier_price = 0

        courier_options = [
            ['Standard Courier', courier_price],
            ['Signed Courier Price', signed_courier_price],
            ['Arrange Pick Up', 0],
        ]

        if economy_price != 0:
            courier_options.append(['Economy', economy_price]) 
    else:
        sub_total_of_stockpile = 0
        gst_of_stockpile = 0
        total_of_stockpile_including_gst = 0
        courier_options = []

        #endregion
    order_request_items_not_yet_stockpiled = order_request_items.filter(
        stockpiled = False) 
    invoices = Invoice.objects.filter(
        member_archived = False,
        member = member)    

    '''#region member's releases, plates and tracks
    member_releases = MemberRelease.objects.filter(member=member)
    member_plates = MemberPlate.objects.filter(member=member).distinct()
    member_tracks = []
    just_tracks = []
    for plate in member_plates:
        vinyl_plate = plate.vinyl_plate
        plate_tracks = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate)
        for track in plate_tracks:
            member_tracks.append([plate.member_release, plate, track, track.crate_id])
            just_tracks.append(track)
    member_tracks = sorted(member_tracks, key=lambda x: x[3])
    #endregion'''
    '''#region crate builder
    potential_crates = []
    for i in just_tracks:
        if i.crate_id not in potential_crates:
            if i.crate_id != '-' and len(i.crate_id) >= 3:
                potential_crates.append(i.crate_id)

    potential_crates = sorted(potential_crates, key=lambda x: x[0])
    set_crate_id_tracks = []
    for i in just_tracks:
        if i.crate_id in potential_crates:
            set_crate_id_tracks.append(i)
    track_count = len(set_crate_id_tracks)
    crate_ids_and_count = []
    for i in potential_crates:
        crate_id_count = 0
        for j in just_tracks:
            if j.crate_id == i:
                crate_id_count += 1
        percentage_of_collection = round(100 / track_count * crate_id_count,3)
        if i == '-':
            crate_id = 'Not Set'
        else:
            crate_id = i
        crate_ids_and_count.append([crate_id, crate_id_count, percentage_of_collection])
    crate_ids_and_count = sorted(crate_ids_and_count, key=lambda x: x[1], reverse=True)
    #endregion'''
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    ''' counts 
    my_library_plates = LibraryPlate.objects.filter(contributor__membership_number='TM1')
    actual_plates_ids = []
    for i in my_library_plates:
        actual_plates_ids.append(i.related_vinyl_plate.pk)
    my_library_plates_count = len(my_library_plates)
    my_releases = []
    for i in my_library_plates:
        if i.related_vinyl_plate.related_release not in my_releases:
            my_releases.append(i.related_vinyl_plate.related_release)
    my_releases_count = len(my_releases)
    '''
    ''' new additions 
    me = Member.objects.get(membership_number='TM1')
    in_collection = MemberReleaseStatusChoices.objects.get(status='In Collection')
    for i in my_releases:
        vinyl_release = VinylRelease.objects.get(catalog_number=i)
        new_member_release = MemberRelease(
            member = me,
            vinyl_release = vinyl_release,
            status = in_collection,
        )
        new_member_release.save()

        vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
        for k in vinyl_plates:
            if k.pk in actual_plates_ids:
                library_plate = my_library_plates.get(related_vinyl_plate=k)
                if len(VinylCondition.objects.filter(condition=library_plate.media_condition)) == 1:
                    vinyl_condition = VinylCondition.objects.get(condition=library_plate.media_condition)
                else:
                    vinyl_condition = None
            else: 
                vinyl_condition = VinylCondition.objects.get(condition='M')
            new_member_plate = MemberPlate(
                member=me,
                member_release=new_member_release,
                vinyl_plate=k,
                vinyl_condition=vinyl_condition,
            )
            new_member_plate.save()

        '''
    context = {
        #region hide
        'library': library,
        'member': member,
        'order_request_items': order_request_items,
        'order_request_items_stockpiled': order_request_items_stockpiled,
        'total_weight_of_stockpile': total_weight_of_stockpile,
        'sub_total_of_stockpile': sub_total_of_stockpile,
        'gst_of_stockpile': gst_of_stockpile,
        'total_of_stockpile_including_gst': total_of_stockpile_including_gst,
        'courier_options': courier_options,
        'order_request_items_not_yet_stockpiled': order_request_items_not_yet_stockpiled,
        'invoices': invoices,
        '''
        'member_releases': member_releases,
        'member_plates': member_plates,
        'member_tracks': member_tracks,
        'potential_crates': potential_crates,
        'crate_ids_and_count': crate_ids_and_count,
        'track_count': track_count,
        '''
        'shopping_cart': shopping_cart,
        'items': items,
        #endregion

    }

    return render(request,'member_dashboard.html', context)

def return_to_member_dashboard(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    order_request_items = OrderRequestItem.objects.filter(
        member = member,
        hidden_from_member = False)

    invoices = Invoice.objects.filter(
        member_archived = False,
        member = member)
    

    current_url = resolve(request.path_info).url_name
    context = {
        'library': library,
        'member': member,
        'order_request_items': order_request_items,
        'invoices': invoices,
        'previous_url': current_url,

    }

    return render(request,'return_to_member_dashboard.html', context)

def members(request, library_id):
    library = Library.objects.get(id=library_id)
    members = Member.objects.filter(library=library).filter(active=True)
    for m in members:
        order_requests = OrderRequest.objects.filter(member=m)
        m.ready_to_ship = OrderRequestItem.objects.filter(
            order_request__member=m).filter(
                sent_to_invoice_receipt=True).filter(
                invoiced=False)
        

    for m in members:
        mpc = len(LibraryPlate.objects.filter(contributor=m))
        mrc = LibraryPlate.objects.filter(contributor=m).values('related_vinyl_plate__related_release__catalog_number').distinct().order_by()
        m.members_plate_count = mpc
        m.members_release_count = len(mrc)
        sub_crate_eye_d = str(m.membership_number) + ' ' + str('On Order') + ' ' + str(library.name)[:3].upper()
        m.sc_count = []
        sub_crates = SubCrate.objects.all()
        for s in sub_crates:
            if s.sub_crate_id == sub_crate_eye_d:
                m.sc_count.append(s)

        if SubCrate.objects.filter(sub_crate_id = str(m.membership_number) + ' ' + str('Stockpile') + ' ' + str(library.name)[:3].upper()):
            members_stockpile_crate = SubCrate.objects.get(sub_crate_id = str(m.membership_number) + ' ' + str('Stockpile') + ' ' + str(library.name)[:3].upper())
            m.members_stockpile_crate = members_stockpile_crate
            members_stockpile_plates = LibraryPlate.objects.filter(related_sub_crate=members_stockpile_crate)
            m.members_stockpile_crate_not_empty = len(members_stockpile_plates)

    context = {
        'library': library,
        'members': members,
    }
    return render(request, 'members.html', context)

def order_request_item_hidden_from_member_submission(request, library_id, order_request_item_id):
    library = Library.objects.get(id=library_id)
    order_request_item = OrderRequestItem.objects.get(id=order_request_item_id)
    order_request_item.hidden_from_member = True
    order_request_item.save()
    context = {
        'library': library,
        'member': order_request_item.order_request.member,
    }
    return render(request, 'return_to_member_dashboard.html', context)

def move_my_library_plates_into_my_collection(request):
    my_library_plates = LibraryPlate.objects.filter(contributor__membership_number='TM1')
    return my_library_plates

#region old views

# member add
def member_add(request, library_id):
    library = Library.objects.get(id=library_id)
    context = {
        'library': library,
    }
    return render(request, 'member_add', context)

# member en_route crate
def member_en_route_crate(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    m_plates = []
    m_ps = LibraryPlate.objects.filter(contributor=member)
    m_sub_crates = SubCrate.objects.filter(sub_crate_id__contains=member.membership_number).filter(sub_crate_id__contains='En Route')
    for i in m_ps:
        for j in m_sub_crates:
            if i.related_sub_crate == j:
                m_plates.append(i)

    _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number).filter(related_sub_crate__sub_crate_id__contains='En Route')     
    track_crate_ids = _m_plates_.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)

    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)

    plate_count = _m_plates_.count()

    ##################
    listerine = []
    for i in track_crate_ids:
        _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number).filter(related_sub_crate__sub_crate_id__contains='En Route').filter(related_vinyl_plate__related_vinyl_track__crate_id=i)
        plate_count = _m_plates_.count()
        listerine.append(str(i) + ' (' + str(plate_count).zfill(3) + ')')
    ##################

    _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number).filter(related_sub_crate__sub_crate_id__contains='En Route')     
    track_crate_ids = _m_plates_.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)

    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)

    plate_count = _m_plates_.count()

    p = Paginator(m_plates, 50)
    page = request.GET.get('page')
    member_plates = p.get_page(page)
    nums = "a" * member_plates.paginator.num_pages

    context = {
        'library': library,
        'listerine': listerine,
        'track_crate_ids': track_crate_ids,
        'plate_count': plate_count,
        'member_plates': member_plates,

        'nums': nums
    }
    return render(request,'member_en_route_crate.html', context)



#region member crates

# member crate add
def member_crate_add(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    library_crate = LibraryCrate.objects.get(library_id=library_id, crate_type='Pending')
    
    member = Member.objects.get(id=member_id)

    member_crate_choices = SubCrate.objects.filter(
        sub_crate_id__icontains=(member.membership_number)).exclude(
        sub_crate_id__icontains=('Stockpile')).exclude(
        sub_crate_id__icontains=('On Order')).exclude(
        sub_crate_id__icontains=('Placing Order')).exclude(
        sub_crate_id__icontains=('Processing Order'))

    
    for i in member_crate_choices:
        i.title = i.sub_crate_id[7:][:-4]

    master_crates = Crate.objects.all().exclude(
        crate_id='Pending').exclude(
        crate_id='Trade').exclude(
        crate_id='To Library').exclude(
        crate_id='Limbo').exclude(
        crate_id='Library to Library').exclude(
        crate_id='On Order').exclude(
        crate_id='Placing Order').exclude(
        crate_id='Stockpile').exclude(
        crate_id='Processing Order')

    for i in member_crate_choices:
        for j in master_crates:
            if i.title == j.crate_id:
                master_crates = master_crates.exclude(crate_id__contains=i.title)


    context = {
        'library':library,
        'library_crate': library_crate,
        'master_crates': master_crates,
        'member': member,
    }
    return render(request,'member_crate_add.html', context)

# member crate add submission
def member_crate_add_submission(request, library_id):
    if request.method == "POST":
        master_library_crate = request.POST['master_library_crate']
        crate_index_start = request.POST['crate_index_start']
        crate_index_end = request.POST['crate_index_end']
        sub_crate_id = request.POST['sub_crate_id']
        obj = SubCrate(
            master_library_crate_id=master_library_crate, crate_index_start=crate_index_start,
            crate_index_end=crate_index_end, sub_crate_id=sub_crate_id, crate_type='Member')
        obj.save()
        member = Member.objects.get(membership_number=sub_crate_id[:6])
        library = Library.objects.get(id=library_id)
        context = {
            'library':library,
            'member': member,
        }
        return render(request, 'return_to_members_crates.html', context)
    return redirect('/')

# member default crates add
def member_default_crates_add(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    
    # member crates
    crates_to_add = ['Limbo', 'Stockpile', 'To Library', 'En Route']
    for crate in crates_to_add:
        master_library_crate_id = LibraryCrate.objects.filter(library_id=library_id).get(library_crate_id__icontains=('Pending')).id
        crate = SubCrate(
            master_library_crate_id = master_library_crate_id,
            crate_index_start = 'A',
            crate_index_end = 'B',
            issued = 'Issued',
            reserved= 'Reserved',
            crate_type = 'Member',
            sub_crate_id = str(member.membership_number) + ' ' + str(crate) + ' ' + str(library.name)[:3].upper()
        )
        crate.save()
    
        
    # admin crates
    crates_to_add = ['On Order', 'Processing Order', 'Placing Order', 'Shipping Requested']
    for crate in crates_to_add:
        master_library_crate_id = LibraryCrate.objects.filter(library_id=library_id).get(library_crate_id__icontains=('Pending')).id
        crate = SubCrate(
            master_library_crate_id = master_library_crate_id,
            crate_index_start = 'A',
            crate_index_end = 'B',
            issued = 'Issued',
            reserved= 'Reserved',
            crate_type = 'Admin',
            sub_crate_id = str(member.membership_number) + ' ' + str(crate) + ' ' + str(library.name)[:3].upper()
        )
        crate.save()
    
    context = {
        'library': library
    }

    return render(request,'return_to_members.html', context)

#endregion


# member plate swap stock for incoming stock
def member_plate_swap_stock_for_incoming_stock(request, library_id, sub_crate_id, plate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library_plate = LibraryPlate.objects.get(id=plate_id)

    if request.method == 'POST':
        library_plate.related_sub_crate_id = request.POST['related_sub_crate_id']
        member_ship_number = SubCrate.objects.filter(
            id=request.POST['related_sub_crate_id']).values_list(
            'sub_crate_id', flat=True)[0][:6]
        receiving_member = Member.objects.get(membership_number=member_ship_number)
        library_plate.contributor = receiving_member

        shop_membership_number = SubCrate.objects.filter(
            id=sub_crate.id).values_list(
            'sub_crate_id', flat=True)[0][:6]
        shops_on_order_sub_crate = SubCrate.objects.filter(sub_crate_id__contains=shop_membership_number).get(sub_crate_id__contains='On Order')
        shop_member = Member.objects.get(membership_number=shop_membership_number)

        on_order_plate = LibraryPlate.objects.filter(
            related_vinyl_plate=library_plate.related_vinyl_plate).get(
            contributor=receiving_member)
        
        on_order_plate.related_sub_crate = shops_on_order_sub_crate
        on_order_plate.contributor = shop_member

        on_order_plate.save()
        library_plate.save()
    
        context = {
            'library': library,
            'sub_crate': sub_crate,
            'member': shop_member,
        }
    
        return render(request, 'return_to_sub_crate.html', context)
    return redirect('/')

# member plate swap stock for incoming stock and delete member plate
## use for situations where you want to change bundle releases for the actual release
def member_plate_swap_stock_for_incoming_stock_and_delete_member_plate(request, library_id, sub_crate_id, plate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library_plate = LibraryPlate.objects.get(id=plate_id)

    if request.method == 'POST':
        library_plate.related_sub_crate_id = request.POST['related_sub_crate_id']
        member_ship_number = SubCrate.objects.filter(
            id=request.POST['related_sub_crate_id']).values_list(
            'sub_crate_id', flat=True)[0][:6]
        receiving_member = Member.objects.get(membership_number=member_ship_number)
        library_plate.contributor = receiving_member

        shop_membership_number = SubCrate.objects.filter(
            id=sub_crate.id).values_list(
            'sub_crate_id', flat=True)[0][:6]
        shops_on_order_sub_crate = SubCrate.objects.filter(sub_crate_id__contains=shop_membership_number).get(sub_crate_id__contains='On Order')
        shop_member = Member.objects.get(membership_number=shop_membership_number)

        on_order_plate = LibraryPlate.objects.filter(
            related_vinyl_plate=library_plate.related_vinyl_plate).get(
            contributor=receiving_member)
        
        on_order_plate.related_sub_crate = shops_on_order_sub_crate
        on_order_plate.contributor = shop_member

        on_order_plate.save()
        library_plate.save()
    
        context = {
            'library': library,
            'sub_crate': sub_crate,
            'member': shop_member,
        }
    
        return render(request, 'return_to_sub_crate.html', context)
    return redirect('/')



# members crates
def members_crates(request, library_id, member_id):
    library = Library.objects.get(id=library_id)

    # member crates
    member = Member.objects.get(id=member_id)
    member_crates = SubCrate.objects.filter(
        sub_crate_id__icontains=(member.membership_number)).exclude(
        sub_crate_id__icontains='Limbo').exclude(
        sub_crate_id__icontains='On Order').exclude(
        sub_crate_id__icontains='Processing Order').exclude(
        sub_crate_id__icontains='Shipping Requested').exclude(
        sub_crate_id__icontains='Placing Order')
    
    master_crates = Crate.objects.all()

    for crate in member_crates:
        crate_plates = LibraryPlate.objects.filter(related_sub_crate=(crate))
        crate.plate_count = crate_plates.count()
    
    special_crates = ['To Library', 'Stockpile', 'Placing Order', 'Limbo', ]    

    for crate in member_crates:
        for special in special_crates:
            if crate.plate_count == 0 and special in crate.sub_crate_id:
                member_crates = member_crates.exclude(sub_crate_id__icontains=(special))
                
    for crate in member_crates:
        crate_plates = LibraryPlate.objects.filter(related_sub_crate=(crate))
        crate.plate_count = crate_plates.count()
    
    for crate in member_crates:
        crate.crate_id = str(crate.sub_crate_id)[7:][:-4]

    for master_crate in master_crates:
        for crate in member_crates:
            if master_crate.crate_id == str(crate.sub_crate_id)[7:][:-4]:
                crate.description = master_crate.description
                if master_crate.genre and master_crate.vibe and master_crate.energy_level:
                    crate.name = master_crate.genre + ' ' + master_crate.vibe + ' ' + master_crate.energy_level
                else:
                    crate.name = crate.crate_id

    limbo_crate = SubCrate.objects.filter(sub_crate_id__contains='Limbo').get(sub_crate_id__contains=member.membership_number)
    limbo_crate_count = len(LibraryPlate.objects.filter(related_sub_crate__sub_crate_id__contains='Limbo').filter(related_sub_crate__sub_crate_id__contains=member.membership_number))
    limbo_crate_description = Crate.objects.get(crate_id='Limbo').description

    # admin crates    
    a_crates = ['Processing Order', 'Placing Order', 'On Order', 'Shipping Requested']    
    
    admin_crates = []
    for i in a_crates:
        c = SubCrate.objects.filter(sub_crate_id__icontains=(member.membership_number)).get(sub_crate_id__icontains=i)
        c.crate_id = str(c.sub_crate_id)[7:][:-4]
        crate_plates = LibraryPlate.objects.filter(related_sub_crate=(c))
        c.plate_count = crate_plates.count()
        admin_crates.append(c)
        
    context = {
        'library':library,
        'member_crates': member_crates,
        'admin_crates': admin_crates,
        'member': member,
        'limbo_crate': limbo_crate,
        'limbo_crate_description': limbo_crate_description,
        'limbo_crate_count': limbo_crate_count
    }
    return render(request,'members_crates.html', context)

# return to members crates
def return_to_members_crates(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    context = {
        'library': library,
        'member': member
    }
    return render(request, 'return_to_members_crates', context)


# member limbo crate
def member_limbo_crate(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    m_plates = []
    m_ps = LibraryPlate.objects.filter(contributor=member)
    m_sub_crates = SubCrate.objects.filter(sub_crate_id__contains=member.membership_number).filter(sub_crate_id__contains='Limbo')
    sub_crate = m_sub_crates.get(sub_crate_id__contains=member.membership_number)
    library_crate = sub_crate.master_library_crate
    for i in m_ps:
        for j in m_sub_crates:
            if i.related_sub_crate == j:
                m_plates.append(i)

    _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number).filter(related_sub_crate__sub_crate_id__contains='Limbo')     
    track_crate_ids = _m_plates_.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)

    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)

    plate_count = _m_plates_.count()

    ##################
    listerine = []
    for i in track_crate_ids:
        _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number).filter(related_sub_crate__sub_crate_id__contains='Limbo').filter(related_vinyl_plate__related_vinyl_track__crate_id=i)
        plate_count = _m_plates_.count()
        listerine.append(str(i) + ' (' + str(plate_count).zfill(3) + ')')
    ##################

    _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number).filter(related_sub_crate__sub_crate_id__contains='Limbo')     
    track_crate_ids = _m_plates_.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)

    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)

    plate_count = _m_plates_.count()

    p = Paginator(m_plates, 50)
    page = request.GET.get('page')
    member_plates = p.get_page(page)
    nums = "a" * member_plates.paginator.num_pages

    

    context = {
        'library': library,
        'sub_crate': sub_crate,
        'library_crate': library_crate,
        'listerine': listerine,
        'track_crate_ids': track_crate_ids,
        'plate_count': plate_count,
        'member_plates': member_plates,
        'nums': nums
    }

    return render(request,'member_limbo_crate.html', context)

# member limbo crate search
def member_limbo_crate_search(request, library_id, member_id):

    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    m_plates = []
    m_ps = LibraryPlate.objects.filter(contributor=member)
    m_sub_crates = SubCrate.objects.filter(sub_crate_id__contains=member.membership_number)
    for i in m_ps:
        for j in m_sub_crates:
            if i.related_sub_crate == j:
                m_plates.append(i)

    _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number).filter(related_sub_crate__sub_crate_id__contains='Limbo')     
    track_crate_ids = _m_plates_.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)

    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)
    
    search_track_crate_id = request.POST['search_track_crate_id']
    search_artist = request.POST['search_artist']
    search_label = request.POST['search_label']
    search_catalog = request.POST['search_catalog']
    if request.POST['search_track_crate_id'] == 'Catergory...':
        search_track_crate_id = search_track_crate_id
    else:
        search_track_crate_id = search_track_crate_id[:-6]

    if search_track_crate_id != 'Catergory...':
        _m_plates_ = _m_plates_.filter(related_vinyl_plate__related_vinyl_track__crate_id__exact=(search_track_crate_id)).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    if search_artist:
        _m_plates_ = _m_plates_.filter(related_vinyl_plate__related_vinyl_track__artist__icontains=(search_artist)).distinct().order_by()   
    if search_label:
        _m_plates_ = _m_plates_.filter(related_vinyl_plate__related_release__label__icontains=(search_label))
    if search_catalog:
        _m_plates_ = _m_plates_.filter(related_vinyl_plate__related_release__catalog_number__icontains=(search_catalog))


    plate_count = _m_plates_.count()

    p = Paginator(_m_plates_, 50)
    page = request.GET.get('page')
    member_plates = p.get_page(page)
    nums = "a" * member_plates.paginator.num_pages

    context = {
        'library': library,
        
        'track_crate_ids': track_crate_ids,

        'plate_count': plate_count,

        'member_plates': member_plates,

        'search_track_crate_id': search_track_crate_id,
        'search_artist': search_artist,
        'search_label': search_label,
        'search_catalog': search_catalog,

        'nums': nums
    }
    return render(request,'member_limbo_crate.html', context)

def member_stockpile(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    members_order_requests = OrderRequest.objects.filter(member=member)
    members_order_request_items = OrderRequestItem.objects.filter(order_request__in=members_order_requests)

    stockpile = members_order_request_items.filter(
        stockpiled=True).filter(
        en_route=False).filter(
        delivered=False).order_by('vinyl_release__catalog_number')

    on_order_plates = members_order_request_items.filter(stockpiled=False).filter(ordered=True).filter(unavailable=False)

    unavailable_releases = members_order_request_items.filter(unavailable=True).filter(date_when_set_to_unavailable__gte=datetime.now()-timedelta(days=14))

    not_ordered_plates = members_order_request_items.filter(ordered=False).filter(unavailable=False)

    #region shipping quote

    total_weight_of_stockpile = 0
    for s in stockpile:
        total_weight_of_stockpile += s.weight_item
    total_weight_of_stockpile = (total_weight_of_stockpile * 25) + 200
    
    address = Address.objects.get(member=member)

    if total_weight_of_stockpile <= 3000:
        if address.island == 'North':
            courier_price = 15 + 2
            economy_price = courier_price - 2
            signed_courier_price = courier_price + 3
        else:
            courier_price = 12 + 2
            economy_price = 0
            signed_courier_price = courier_price + 3

    elif total_weight_of_stockpile <= 10000:
        if address.island == 'North':
            courier_price = 74 + 2
            economy_price = 0
            signed_courier_price = courier_price + 3
        else:
            courier_price = 24 + 2
            economy_price = 0
            signed_courier_price = courier_price + 3
    else:
        courier_price = 0
        economy_price = 0
        signed_courier_price = 0

    #endregion
        
    context = {
        'library': library,
        'member': member,
        'stockpile': stockpile,
        'on_order_plates': on_order_plates,
        'not_ordered_plates': not_ordered_plates,
        'unavailable_releases': unavailable_releases,

        'total_weight_of_stockpile': total_weight_of_stockpile,
        'courier_price': courier_price,
        'economy_price': economy_price,
        
        'signed_courier_price': signed_courier_price,
    }
    return render(request,'member_stockpile.html', context)

def member_stockpile_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(membership_number=request.POST['membership_number'])
    members_order_requests = OrderRequest.objects.filter(member=member)
    members_order_request_items = OrderRequestItem.objects.filter(order_request__in=members_order_requests)

    stockpile = members_order_request_items.filter(
        stockpiled=True).filter(
        en_route=False).filter(
        delivered=False).order_by('vinyl_release__catalog_number')

    on_order_plates = members_order_request_items.filter(stockpiled=False).filter(ordered=True).filter(unavailable=False)

    unavailable_releases = members_order_request_items.filter(unavailable=True).filter(date_when_set_to_unavailable__gte=datetime.now()-timedelta(days=14))

    not_ordered_plates = members_order_request_items.filter(ordered=False).filter(unavailable=False)

    #region shipping quote

    total_weight_of_stockpile = 0
    for s in stockpile:
        total_weight_of_stockpile += s.weight_item
    total_weight_of_stockpile = (total_weight_of_stockpile * 25) + 200
    
    address = Address.objects.get(member=member)

    if total_weight_of_stockpile <= 3000:
        if address.island == 'North':
            courier_price = 15 + 2
            economy_price = courier_price - 2
            signed_courier_price = courier_price + 3
        else:
            courier_price = 12 + 2
            economy_price = 0
            signed_courier_price = courier_price + 3

    elif total_weight_of_stockpile <= 10000:
        if address.island == 'North':
            courier_price = 74 + 2
            economy_price = 0
            signed_courier_price = courier_price + 3
        else:
            courier_price = 24 + 2
            economy_price = 0
            signed_courier_price = courier_price + 3
    else:
        courier_price = 0
        economy_price = 0
        signed_courier_price = 0

    #endregion
        
    context = {
        'library': library,
        'member': member,
        'stockpile': stockpile,
        'on_order_plates': on_order_plates,
        'not_ordered_plates': not_ordered_plates,
        'unavailable_releases': unavailable_releases,

        'total_weight_of_stockpile': total_weight_of_stockpile,
        'courier_price': courier_price,
        'economy_price': economy_price,
        
        'signed_courier_price': signed_courier_price,
    }
    return render(request,'member_stockpile.html', context)

# return to member stockpile crate
def return_to_member_stockpile_crate(request, library_id, sub_crate_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    context = {
        'library': library,
        'member': member,
        'sub_crate': sub_crate
    }
    return render(request, 'return_to_member_stockpile_crate', context)

# return to member limbo crate
def return_to_member_limbo_crate(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    context = {
        'library': library,
        'member': member
    }
    return render(request, 'return_to_member_limbo_crate', context)

#region member credit

def member_credit_account(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)

    context = {
        'library':library,
        'member': member,
    }
    
    return render(request,'member_credit_account.html', context)

def member_credit_account_submission(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)

    credit_amount = Decimal(request.POST['credit_amount'])

    member.account_credit += credit_amount
    member.save()
    
    context = {
        'library':library,
        'member': member,
    }

    return render(request, 'return_to_members.html', context)

#endregion

#region members plate move

# member plate move
def member_plate_move(request, library_id, sub_crate_id, plate_id, previous_url):
    library = Library.objects.get(id=library_id)    
    library_plate_member = LibraryPlate.objects.get(id=plate_id).contributor.id
    member = Member.objects.get(id=library_plate_member)

    member_crate_choices = SubCrate.objects.filter(
        sub_crate_id__icontains=(member.membership_number)).exclude(
        sub_crate_id__icontains=('Stockpile')).exclude(
        sub_crate_id__icontains=('On Order')).exclude(
        sub_crate_id__icontains=('Placing Order')).exclude(
        sub_crate_id__icontains=('Processing Order')).exclude(
        sub_crate_id__icontains=('Shipping Requested')).exclude(
        sub_crate_id__icontains=('En Route'))
 
    for i in member_crate_choices:
        i.title = i.sub_crate_id[7:][:-4]

    librarians_crate_choices = [
        'Placing Order',
        'Processing Order',
        'On Order',
        'Stockpile',
        'En Route',
        'Shipping Requested',
    ]

    librarian_crate_choices = []
    for i in librarians_crate_choices:
        choice = SubCrate.objects.filter(
            sub_crate_id__icontains=(member.membership_number)).get(
            sub_crate_id__icontains=(i))
        choice.title = choice.sub_crate_id[7:][:-4]
        librarian_crate_choices.append(choice)

    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    sub_crate.title = sub_crate.sub_crate_id[7:][:-4]
    library_plate = LibraryPlate.objects.get(id=plate_id)

    pending_crate = LibraryCrate.objects.get(library_id=library_id, crate_type='Pending')
    master_crates = Crate.objects.all().exclude(
        crate_id='Pending').exclude(
        crate_id='Trade').exclude(
        crate_id='To Library').exclude(
        crate_id='Limbo').exclude(
        crate_id='Library to Library').exclude(
        crate_id='On Order').exclude(
        crate_id='Placing Order').exclude(
        crate_id='Stockpile').exclude(
        crate_id='Processing Order').exclude(
        crate_id='En Route').exclude(
        crate_id='Shipping Requested')

    for i in member_crate_choices:
        for j in master_crates:
            if i.title == j.crate_id:
                master_crates = master_crates.exclude(crate_id__contains=i.title)

    advanced_sub_crate_options = SubCrate.objects.filter(
        master_library_crate__library=library).exclude(
        master_library_crate__crate_type='Mix').exclude(
        sub_crate_id__icontains='Shipping Requested').exclude(
        sub_crate_id__icontains='En Route').exclude(
        sub_crate_id__icontains='Placing Order').exclude(
        sub_crate_id__icontains='Processing Order')
    
    members = Member.objects.filter(library=library)

    move_and_swap_crates = SubCrate.objects.filter(
        master_library_crate__library=library).filter(
        sub_crate_id__icontains='Stockpile')
    
    context = {
        'library': library,
        'pending_crate': pending_crate,
        'member_crate_choices': member_crate_choices,
        'master_crates': master_crates,
        'librarian_crate_choices': librarian_crate_choices,
        'advanced_sub_crate_options': advanced_sub_crate_options,
        'members': members,
        'sub_crate': sub_crate,
        'library_plate': library_plate,
        'previous_url': previous_url,
        'member': member,
        'move_and_swap_crates': move_and_swap_crates,
    }
    return render(request,'member_plate_move.html', context)

# member plate move submission
def member_plate_move_submission(request, library_id, sub_crate_id, plate_id):
    if request.method == 'POST':
        library = Library.objects.get(id=library_id)
        sub_crate = SubCrate.objects.get(id=sub_crate_id)
        library_plate = LibraryPlate.objects.get(id=plate_id)

        sub_crate_title = request.POST['related_sub_crate_id']
        related_sub_crate = SubCrate.objects.filter(
            sub_crate_id__contains=sub_crate_title).get(
            sub_crate_id__contains=sub_crate.sub_crate_id[:6])

        library_plate.related_sub_crate = related_sub_crate
        library_plate.save()
    
        context = {
            'library': library,
            'sub_crate': sub_crate,
            'member': library_plate.contributor
        }
        if 'Limbo' in sub_crate.sub_crate_id:
            return render(request, 'return_to_member_limbo_crate.html', context)
        if 'En Route' in sub_crate.sub_crate_id:
            return render(request, 'return_to_member_en_route_crate.html', context)
        else:
            return render(request, 'return_to_members_crates.html', context)
    return redirect('/')

# member plate advanced move submission
def member_plate_advanced_move_submission(request, library_id, sub_crate_id, plate_id):
    if request.method == 'POST':
        library = Library.objects.get(id=library_id)
        sub_crate = SubCrate.objects.get(id=sub_crate_id)
        library_plate = LibraryPlate.objects.get(id=plate_id)

        library_plate.related_sub_crate_id = request.POST['related_sub_crate_id']
        library_plate.contributor_id = request.POST['member']
        library_plate.save()
    
        context = {
            'library': library,
            'sub_crate': sub_crate,
            'member': library_plate.contributor,
        }
    
        return render(request, 'return_to_sub_crate.html', context)
    return redirect('/')

# member plate move to limbo submission
def member_plate_move_to_limbo_submission(request, library_id, sub_crate_id, plate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library_plate = LibraryPlate.objects.get(id=plate_id)
    library_plate.related_sub_crate_id = SubCrate.objects.filter(sub_crate_id__contains=library_plate.contributor.membership_number).get(sub_crate_id__contains='Limbo')
    library_plate.recieved = True
    library_plate.save()

    context = {
        'library': library,
        'sub_crate': sub_crate,
        'member': library_plate.contributor
    }

    return render(request, 'return_to_member_stockpile_crate.html', context)

# member plate move to en route submission
def member_plate_move_to_en_route_submission(request, library_id, sub_crate_id, plate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library_plate = LibraryPlate.objects.get(id=plate_id)
    library_plate.related_sub_crate_id = SubCrate.objects.filter(sub_crate_id__contains=library_plate.contributor.membership_number).get(sub_crate_id__contains='En Route')
    library_plate.save()

    context = {
        'library': library,
        'sub_crate': sub_crate,
        'member': library_plate.contributor
    }

    return render(request, 'return_to_member_stockpile_crate.html', context)

# member crate add and move submission
def member_crate_add_and_move_submission(request, library_id, plate_id):
    if request.method == "POST":
        master_library_crate = request.POST['master_library_crate']
        crate_index_start = request.POST['crate_index_start']
        crate_index_end = request.POST['crate_index_end']
        sub_crate_id = request.POST['sub_crate_id']
        obj = SubCrate(
            master_library_crate_id=master_library_crate, crate_index_start=crate_index_start,
            crate_index_end=crate_index_end, sub_crate_id=sub_crate_id, crate_type='Member')
        obj.save()
        
        library_plate = LibraryPlate.objects.get(id=plate_id)
        library_plate.related_sub_crate = SubCrate.objects.get(sub_crate_id=sub_crate_id)
        library_plate.save()

        library = Library.objects.get(id=library_id)
        context = {
            'library':library,
            'member': library_plate.contributor,
        }
        return render(request, 'return_to_members_crates.html', context)
    return redirect('/')

#endregion

#region members want list functions

# release add to members maybe list submission
def release_add_to_members_maybe_list_submission(request, library_id, release_id, member_id, previous_url):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    member_unwanted_list = MemberMaybeList.objects.get(member=member)
    release = VinylRelease.objects.get(id=release_id)
    member_unwanted_list.maybe_list.add(release)

    context = {
        'library': library,
        'release': release,
        'previous_url': previous_url,
    }

    if 'database' in previous_url:
        going_to = 'return_to_release_database.html'
    elif 'vinyl_ordering' in previous_url:
        going_to = 'return_to_vinyl_shop.html'
    elif 'compile' in previous_url:
        going_to = 'return_to_release_compile.html'
    elif 'release' in previous_url:
        going_to = 'return_to_release.html'

    return render(request, going_to, context)

# release remove from members maybe list submission
def release_remove_from_members_maybe_list_submission(request, library_id, release_id, member_id, previous_url):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    member_unwanted_list = MemberMaybeList.objects.get(member=member)
    release = VinylRelease.objects.get(id=release_id)
    member_unwanted_list.maybe_list.remove(release)

    context = {
        'library': library,
        'release': release,
        'previous_url': previous_url,
    }

    if 'database' in previous_url:
        going_to = 'return_to_release_database.html'
    elif 'vinyl_ordering' in previous_url:
        going_to = 'return_to_vinyl_shop.html'
    elif 'compile' in previous_url:
        going_to = 'return_to_release_compile.html'
    elif 'release' in previous_url:
        going_to = 'return_to_release.html'

    return render(request, going_to, context)


# release add to members unwanted list submission
def release_add_to_members_unwanted_list_submission(request, library_id, release_id, member_id, previous_url):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    member_unwanted_list = MemberUnwantedList.objects.get(member=member)
    release = VinylRelease.objects.get(id=release_id)
    member_unwanted_list.unwanted_list.add(release)

    context = {
        'library': library,
        'release': release,
        'previous_url': previous_url,
    }

    if 'database' in previous_url:
        going_to = 'return_to_release_database.html'
    elif 'vinyl_ordering' in previous_url:
        going_to = 'return_to_vinyl_shop.html'
    elif 'compile' in previous_url:
        going_to = 'return_to_release_compile.html'
    elif 'release' in previous_url:
        going_to = 'return_to_release.html'

    return render(request, going_to, context)

# release remove from members unwanted list submission
def release_remove_from_members_unwanted_list_submission(request, library_id, release_id, member_id, previous_url):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    member_unwanted_list = MemberUnwantedList.objects.get(member=member)
    release = VinylRelease.objects.get(id=release_id)
    member_unwanted_list.unwanted_list.remove(release)

    context = {
        'library': library,
        'release': release,
        'previous_url': previous_url,
    }

    if 'database' in previous_url:
        going_to = 'return_to_release_database.html'
    elif 'vinyl_ordering' in previous_url:
        going_to = 'return_to_vinyl_shop.html'
    elif 'compile' in previous_url:
        going_to = 'return_to_release_compile.html'
    elif 'release' in previous_url:
        going_to = 'return_to_release.html'

    return render(request, going_to, context)

# release add to members wantlist submission
def release_add_to_members_wantlist_submission(request, library_id, release_id, member_id, previous_url):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    member_want_list = MemberWantlist.objects.get(member=member)
    release = VinylRelease.objects.get(id=release_id)
    member_want_list.want_list.add(release)

    context = {
        'library': library,
        'release': release,
    }

    if 'database' in previous_url:
        going_to = 'return_to_release_database.html'
    elif 'vinyl_ordering' in previous_url:
        going_to = 'return_to_vinyl_shop.html'
    elif 'compile' in previous_url:
        going_to = 'return_to_release_compile.html'
    elif 'release' in previous_url:
        going_to = 'return_to_release.html'

    return render(request, going_to, context)

# release remove to members wantlist submission
def release_remove_to_members_wantlist_submission(request, library_id, release_id, member_id, previous_url):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    member_want_list = MemberWantlist.objects.get(member=member)
    release = VinylRelease.objects.get(id=release_id)
    member_want_list.want_list.remove(release)

    context = {
        'library': library,
        'release': release,
        'previous_url': previous_url,
    }

    if 'database' in previous_url:
        going_to = 'return_to_release_database.html'
    elif 'compile' in previous_url:
        going_to = 'return_to_release_compile.html'
    elif 'vinyl_ordering' in previous_url:
        going_to = 'return_to_vinyl_shop.html'
    elif 'release' in previous_url:
        going_to = 'return_to_release.html'

    return render(request, going_to, context)

#endregion

#endregion


#region unused
'''
# member personal plates
def member_personal_plates(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    m_plates = []
    m_ps = LibraryPlate.objects.filter(contributor=member)
    m_sub_crates = SubCrate.objects.filter(sub_crate_id__contains=member.membership_number).filter(sub_crate_id__contains='Limbo')
    for i in m_ps:
        for j in m_sub_crates:
            if i.related_sub_crate == j:
                m_plates.append(i)

    _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number).filter(related_sub_crate__sub_crate_id__contains='Limbo')     
    track_crate_ids = _m_plates_.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)
    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)

    plate_count = _m_plates_.count()

    p = Paginator(m_plates, 50)
    page = request.GET.get('page')
    member_plates = p.get_page(page)
    nums = "a" * member_plates.paginator.num_pages

    context = {
        'library': library,
        
        'track_crate_ids': track_crate_ids,

        'plate_count': plate_count,

        'member_plates': member_plates,

        'nums': nums
    }
    return render(request,'member_personal_plates.html', context)

# member plate search
def member_personal_plates_search(request, library_id, member_id):

    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    m_plates = []
    m_ps = LibraryPlate.objects.filter(contributor=member)
    m_sub_crates = SubCrate.objects.filter(sub_crate_id__contains=member.membership_number)
    for i in m_ps:
        for j in m_sub_crates:
            if i.related_sub_crate == j:
                m_plates.append(i)

    _m_plates_ = LibraryPlate.objects.filter(contributor=member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number)       
    track_crate_ids = _m_plates_.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)
    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)


    search_track_crate_id = request.POST['search_track_crate_id']
    search_artist = request.POST['search_artist']
    search_label = request.POST['search_label']
    search_catalog = request.POST['search_catalog']

    if search_track_crate_id != 'Catergory...':
        _m_plates_ = _m_plates_.filter(related_vinyl_plate__related_vinyl_track__crate_id__exact=(search_track_crate_id)).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    if search_artist:
        _m_plates_ = _m_plates_.filter(related_vinyl_plate__related_vinyl_track__artist__icontains=(search_artist)).distinct().order_by()   
    if search_label:
        _m_plates_ = _m_plates_.filter(related_vinyl_plate__related_release__label__icontains=(search_label))
    if search_catalog:
        _m_plates_ = _m_plates_.filter(related_vinyl_plate__related_release__catalog_number__icontains=(search_catalog))




    plate_count = _m_plates_.count()

    p = Paginator(_m_plates_, 50)
    page = request.GET.get('page')
    member_plates = p.get_page(page)
    nums = "a" * member_plates.paginator.num_pages




    context = {
        'library': library,
        
        'track_crate_ids': track_crate_ids,

        'plate_count': plate_count,

        'member_plates': member_plates,

        'search_track_crate_id': search_track_crate_id,
        'search_artist': search_artist,
        'search_label': search_label,
        'search_catalog': search_catalog,

        'nums': nums
    }
    return render(request,'member_personal_plates.html', context)
'''
#endregion