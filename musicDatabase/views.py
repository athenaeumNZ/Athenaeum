import csv
from django.contrib import messages
from decimal import Decimal
from io import BytesIO
import os
from uuid import uuid4
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.urls import resolve
from django.core.files.base import ContentFile
from PIL import Image
from django.core.files import File
from accounts.models import OrderRequestItem

from cart.cart import Cart
from choices.models import Genre
from management.models import Member, VinylIndex, Vibe, EnergyLevel, Country, Library, VinylColour, VinylSleeveType, VinylReleaseType, VinylPlateSize
from musicDatabase.models import VinylPlate, VinylRelease, VinylReleaseRepressRequest, VinylTrack, VinylDistributor
from musicDatabase.utils import vinyl_release_average_tracks_per_side_util
from shoppingCart.shopping_cart import ShoppingCart
from crateBuilder.views import *
from vinylShop.models import StockItem

def vinyl_release(request, library_id):
    library = Library.objects.get(id=library_id)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    current_url = resolve(request.path_info).url_name
    context = {
        'library': library,
        'previous_url': current_url,
        'shopping_cart': shopping_cart,
        'items': items,
    }
    form_variables(request, context)
    form_search_variables(request, context)
    if request.POST['member_id'] != '':
        member = Member.objects.get(id=request.POST['member_id'])
    else:
        member = None
    vinyl_release = VinylRelease.objects.get(id=request.POST['vinyl_release_id'])
    vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
    all_plates = []
    for i in vinyl_plates:
        vinyl_plate = i
        vinyl_plate_identifier = str(vinyl_release) + str(vinyl_plate.plate_index)
        if len(MemberPlate.objects.filter(member=member, vinyl_plate=vinyl_plate)) == 1:
            member_plate = MemberPlate.objects.get(member=member, vinyl_plate=vinyl_plate)
        else:
            member_plate = None
        if len(StockItem.objects.filter(library=library, vinyl_release=vinyl_release)) >= 1:
            stock_item = StockItem.objects.get(library = library, vinyl_release = vinyl_plate.related_release)
        else:
            stock_item = None
        release_title_long = str(vinyl_release.artist) + ' - ' + str(vinyl_release.release_title) + ' - ' + str(vinyl_release.label)
        if len(release_title_long) >= 60:
            release_title_long = release_title_long[:60] + '...'
        else:
            release_title_long = release_title_long
        vinyl_tracks_crate_ids = VinylTrack.objects.filter(related_vinyl_plate=vinyl_plate).values_list('crate_id', flat=True).filter(crate_id__isnull=False)
        vinyl_tracks_crate_ids = by_size(vinyl_tracks_crate_ids,4)
        vinyl_tracks_crate_ids = sorted(vinyl_tracks_crate_ids, key=lambda x: x[0])
        vinyl_tracks_crate_ids = list(dict.fromkeys(vinyl_tracks_crate_ids))
        all_plates.append([vinyl_plate_identifier, member_plate, vinyl_plate, stock_item, release_title_long, vinyl_tracks_crate_ids,])
    all_plates = sorted(all_plates, key=lambda x: x[0])
    in_collection = MemberReleaseStatusChoices.objects.get(status='In Collection')
    in_coming = MemberReleaseStatusChoices.objects.get(status='In Coming')
    crate_parents = CrateParent.objects.filter(member=member)
    crate_parents_crate_ids = []
    for i in crate_parents:
        crate_parents_crate_ids.append(i.crate_id)
    context['in_coming'] = in_coming
    context['in_collection'] = in_collection
    context['all_plates'] = all_plates
    context['crate_parents'] = crate_parents
    
    return render(request,'vinyl_release.html', context)

    









def return_to_vinyl_release(request, library_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=request.POST['release_id'])
    in_stock_items = StockItem.objects.filter(vinyl_release=release)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    current_url = resolve(request.path_info).url_name
    context = {
        'library': library,
        'release': release,
        'in_stock_items': in_stock_items,
        'previous_url': current_url,
        'shopping_cart': shopping_cart,
        'items': items,
    }
    form_variables(request, context)
    form_search_variables(request, context)
    return render(request,'return_to_vinyl_release.html', context)










#region release
def release(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    in_stock_items = StockItem.objects.filter(vinyl_release=release)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    current_url = resolve(request.path_info).url_name
    context = {
        'library': library,
        'release': release,
        'in_stock_items': in_stock_items,
        'previous_url': current_url,
        'shopping_cart': shopping_cart,
        'items': items,
    }
    if 'member_id' in request.POST:
        context['member_id'] = Member.objects.get(id=request.POST['member_id'])
    if 'crate_id' in request.POST:
        context['crate_id'] = request.POST['crate_id']
    if 'crate_parent_id' in request.POST:
        context['crate_parent_id'] = request.POST['crate_parent_id']
    if 'display_stock' in request.POST:
        context['display_stock'] = request.POST['display_stock']
    if 'display_unallocated' in request.POST:
        context['display_unallocated'] = request.POST['display_unallocated']
    if 'display_searched_releases' in request.POST:
        context['display_searched_releases'] = request.POST['display_searched_releases']
    if 'previous_vertical_location' in request.POST:
        context['previous_vertical_location'] = request.POST['previous_vertical_location']

    return render(request,'release.html', context)

def vinyl_release_add_check_catalog_number(request, library_id):
    library = Library.objects.get(id=library_id)
    context = {
        'library': library,
    }
    return render(request,'vinyl_release_add_check_catalog_number.html', context)

def vinyl_release_add_check_catalog_number_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    catalog_number = request.POST['catalog_number']
    if len(VinylRelease.objects.filter(catalog_number=catalog_number)) >= 1:
        vinyl_release = VinylRelease.objects.get(catalog_number=catalog_number)
        context = {
            'library': library,
            'vinyl_release': vinyl_release,
        }
        return render(request,'return_to_vinyl_release.html', context)
    else:
        context = {
            'library': library,
            'catalog_number': catalog_number,
        }
        return render(request,'return_to_vinyl_release_add.html', context)

def vinyl_release_add(request, library_id, catalog_number):
    library = Library.objects.get(id=library_id)
    countries = Country.objects.all()
    vinyl_colours = VinylColour.objects.all()
    release_types = VinylReleaseType.objects.all()
    sleeve_types = VinylSleeveType.objects.all()
    plate_sizes = VinylPlateSize.objects.all()
    distributors = VinylDistributor.objects.filter(active=True) | VinylDistributor.objects.filter(name='No Known Distributor')
    distributors = distributors.order_by('name')
    genres = Genre.objects.all()

    context = {
        'library': library,
        'catalog_number': catalog_number,
        'countries': countries,
        'vinyl_colours': vinyl_colours,
        'release_types': release_types,
        'sleeve_types': sleeve_types,
        'plate_sizes': plate_sizes,
        'distributors': distributors,
        'genres': genres,
    }
    return render(request,'vinyl_release_add.html', context)

def vinyl_release_add_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    if request.method == 'POST' and 'FILES':
        catalog_number = str(request.POST['catalog_number']).strip()
        artist = str(request.POST['artist']).strip().replace(
            'Dj', 'DJ').replace(
            'dj', 'DJ').replace(
            'V/A', 'Various Artists').replace(
            'Various', 'Various Artists').replace(
            'Various Artists Artists', 'Various Artists').replace(
            'VARIOUS', 'Various Artists').replace(
            'Feat', 'feat').replace(
            'Feat', 'feat').replace(
            'FEAT', 'feat')
        artist = artist
        if str(request.POST['release_title']).strip() == str(request.POST['catalog_number']).strip():
            release_title = str(request.POST['release_title']).strip()
        else:
            release_title = " ".join([word.title() if word not in "EP VIP DJ a" else word for word in str(request.POST['release_title']).split(" ")]).strip()
        label = str(request.POST['label']).strip()
        plate_size = request.POST['plate_size']
        if str(plate_size) == 'Choose...':
            plate_size = '12"'
        plate_count = request.POST['plate_count']
        
        if request.POST['distributor']!= None and request.POST['distributor']!= 'Choose...':
            distributor_id = request.POST['distributor']
        else:
            no_known_distributor = VinylDistributor.objects.get(name='No Known Distributor')
            distributor_id = no_known_distributor.pk
        #region create vinyl_release required fields
        vinyl_release = VinylRelease(
            catalog_number=catalog_number,
            artist=artist, 
            release_title=release_title,
            label=label,
            plate_size=plate_size,
            plate_count=plate_count,
            distributor_id=distributor_id,
            )
        vinyl_release.save()
        if request.POST['release_date'] == "":
            vinyl_release.release_date_tbc = True
            vinyl_release.save()
        else:
            vinyl_release.release_date = request.POST['release_date']
            vinyl_release.save()
        #endregion
        #region optional fields
        if request.FILES.get('artwork') != None:
            vinyl_release.artwork = request.FILES.get('artwork')
            vinyl_release.save()
        if vinyl_release.artwork:
            _, ext = os.path.splitext(vinyl_release.artwork.path)
            image = Image.open(vinyl_release.artwork.path)
            source_image = image.convert('RGB')
            source_image.thumbnail((100, 100))
            output = BytesIO()
            source_image.save(output, format='JPEG')
            output.seek(0)
            content_file = ContentFile(output.read())
            file = File(content_file)
            name = f'{uuid4()}{ext}'
            vinyl_release.artwork_small.save(name, file, save=True)
        if request.POST['stock_estimation']!= None and request.POST['stock_estimation'] != '':
            vinyl_release.stock_estimation = request.POST['stock_estimation']
            vinyl_release.save()
        else:
            vinyl_release.stock_estimation = 30
            vinyl_release.save()
        if request.POST['not_black'] != 'Choose...' and request.POST['not_black'] != 'None':
            vinyl_release.not_black = request.POST['not_black']
            vinyl_release.save()
        if request.POST['cost_price']!= None and request.POST['cost_price']!= '':
            vinyl_release.cost_price = request.POST['cost_price']
            vinyl_release.save()
        else:
            vinyl_release.cost_price = Decimal(999.99)
            vinyl_release.save()
        if request.POST['set_to_not_on_previous_weekly_release_sheet'] == 'True':
            vinyl_release.on_previous_weekly_release_sheet = False
            vinyl_release.save()
        if request.POST['master_genre_id'] != 'Choose...':
            vinyl_release.master_genre = Genre.objects.get(id=request.POST['master_genre_id'])
            vinyl_release.save()
        #endregion
        #region Create Plates
        plate_count = Decimal(plate_count)
        if plate_count >= 1:
            plate_index = 'a/b'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 2:
            plate_index = 'c/d'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 3:
            plate_index = 'e/f'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 4:
            plate_index = 'g/h'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 5:
            plate_index = 'i/j'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 6:
            plate_index = 'k/l'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 7:
            plate_index = 'm/n'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 8:
            plate_index = 'o/p'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 9:
            plate_index = 'q/r'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 10:
            plate_index = 's/t'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 11:
            plate_index = 'u/v'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 12:
            plate_index = 'w/x'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        if plate_count >= 13:
            plate_index = 'y/z'
            obj = VinylPlate(
                related_release=vinyl_release, plate_index=plate_index)
            obj.save()
        #endregion
        first_plate = VinylPlate.objects.filter(related_release=vinyl_release).first()
        release = VinylRelease.objects.get(catalog_number=catalog_number)
        context = {
            'library': library,
            'release': release,
            'first_plate': first_plate,
        }
        return render(request, 'track_add_go_to_first_track_add.html', context)
    return redirect('/')

def return_to_release(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)

    context = {
        'library': library,
        'release': release,
    }

    return render(request,'return_to_release.html', context)

def return_to_vinyl_release_add(request, library_id, catalog_number):
    library = Library.objects.get(id=library_id)

    context = {
        'library': library,
        'catalog_number': catalog_number,
    }

    return render(request,'return_to_vinyl_release_add.html', context)

def release_request_repress_submission(request, library_id, ):
    library = Library.objects.get(id=library_id)
    vinyl_release = request.POST['vinyl_release']
    member = request.POST['member']
    old_request_request = VinylReleaseRepressRequest.objects.filter(
        vinyl_release=vinyl_release,
        member=member)
    if old_request_request != None and len(old_request_request) >= 1:
        old_request_request[0].delete(0)

    new_repress_request = VinylReleaseRepressRequest(
        vinyl_release_id = vinyl_release,
        member_id = member,
    )   
    new_repress_request.save()
        
    context = {
        'library': library,
    }
    return render(request, 'return_to_vinyl_shop.html', context)
#endregion

#region release compile
    # need to be able to move tracks between plates
def release_compile(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    in_stock_items = StockItem.objects.filter(vinyl_release=release)
    in_stock_at_my_library_quantity = len(in_stock_items.filter(library=library))

    in_coming_items = OrderRequestItem.objects.filter(
        member__is_library_shop=True, vinyl_release=release)

    cart = Cart(request)
    items = cart.items_list
    current_url = resolve(request.path_info).url_name # current_url

    context = {
        'library': library,
        'release': release,
        'in_stock_items': in_stock_items,
        'in_stock_at_my_library_quantity': in_stock_at_my_library_quantity,
        'in_coming_items': in_coming_items,
        'previous_url': current_url,
        'cart': cart,
        'items': items,
    }

    return render(request,'release_compile.html', context)

def release_delete(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    context = {
        'library': library,
        'release': release
    }
    return render(request, 'release_delete.html', context)

def release_delete_submission(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    release.delete()
    context = {
        'library': library,
    }
    return render(request, 'return_to_vinyl_shop.html', context)

def release_edit(request, library_id, release_id, catalog_number_to_check):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    countries = Country.objects.all()
    vinyl_colours = VinylColour.objects.all()
    release_types = VinylReleaseType.objects.all()
    sleeve_types = VinylSleeveType.objects.all()
    plate_sizes = VinylPlateSize.objects.all()
    distributors = VinylDistributor.objects.filter(active=True) | VinylDistributor.objects.filter(name='No Known Distributor')
    distributors = distributors.order_by('name')
    catalog_number_to_check = catalog_number_to_check
    genres = Genre.objects.all()

    context = {
        'library': library,
        'release': release,
        'countries': countries,
        'vinyl_colours': vinyl_colours,
        'release_types': release_types,
        'sleeve_types': sleeve_types,
        'plate_sizes': plate_sizes,
        'distributors': distributors,
        'catalog_number_to_check': catalog_number_to_check,
        'genres': genres,
    }
    return render(request,'vinyl_release_add.html', context)

def release_edit_submission(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    vinyl_release = VinylRelease.objects.get(id=release_id)
    if request.method == 'POST' and 'FILES':
        vinyl_release.catalog_number = request.POST['catalog_number']
        vinyl_release.artist = request.POST['artist']
        vinyl_release.release_title = request.POST['release_title']
        vinyl_release.label = request.POST['label']
        vinyl_release.release_date = request.POST['release_date']
        vinyl_release.plate_size = request.POST['plate_size']
        vinyl_release.plate_count = request.POST['plate_count']
        vinyl_release.distributor = VinylDistributor.objects.get(id=request.POST['distributor'])
        vinyl_release.stock_estimation = request.POST['stock_estimation']
        vinyl_release.cost_price = request.POST['cost_price']
        if request.FILES.get('artwork') != None:
            vinyl_release.artwork = request.FILES.get('artwork')
            vinyl_release.save()
            _, ext = os.path.splitext(vinyl_release.artwork.path)
            image = Image.open(vinyl_release.artwork.path)
            source_image = image.convert('RGB')
            source_image.thumbnail((100, 100))
            output = BytesIO()
            source_image.save(output, format='JPEG')
            output.seek(0)
            content_file = ContentFile(output.read())
            file = File(content_file)
            name = f'{uuid4()}{ext}'
            vinyl_release.artwork_small.save(name, file, save=True)
        vinyl_release.save()
        if request.POST['set_to_not_on_previous_weekly_release_sheet'] == 'True':
            vinyl_release.on_previous_weekly_release_sheet = False
            vinyl_release.save()
        if request.POST['master_genre_id'] != 'Choose...':
            vinyl_release.master_genre = Genre.objects.get(id=request.POST['master_genre_id'])
            vinyl_release.save()
        if request.POST['not_black'] != 'Choose...' and request.POST['not_black'] != 'None':
            vinyl_release.not_black = request.POST['not_black']
            vinyl_release.save()

        context = {
            'library': library,
            'release': vinyl_release,
        }
        previous_plate_count = request.POST['previous_plate_count']
        if vinyl_release.plate_count != previous_plate_count:
            message  = messages.error(request, "Warning! The plate count has changed for this release. You will need to manually move tracks around etc." )
            context['message'] = message
        vinyl_release_average_tracks_per_side_util(vinyl_release)
        return render(request, 'return_to_release_compile.html', context)
    return redirect('/')

def release_plate_add(request, library_id, release_id):# UNUSED
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    indexes = VinylIndex.objects.all()
    context = {
        'library': library,
        'release': release,
        'indexes': indexes
    }
    return render(request,'release_plate_add.html', context)

def release_plate_add_function(release_id, pre_context):
    vinyl_release = VinylRelease.objects.get(id=release_id)
    current_plates = VinylPlate.objects.filter(related_release=vinyl_release)
    last_plate = []
    if len(current_plates) == 0:
        last_plate = None
    else:
        last_plate = current_plates.last()
    if last_plate == None:
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='a/b')
        new_plate.save()
    elif last_plate.plate_index =='a/b':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='c/d')
        new_plate.save()
    elif last_plate.plate_index =='c/d':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='e/f')
        new_plate.save()
    elif last_plate.plate_index =='e/f':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='g/h')
        new_plate.save()
    elif last_plate.plate_index =='g/h':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='i/j')
        new_plate.save()        
    elif last_plate.plate_index =='i/j':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='k/l')
        new_plate.save()                
    elif last_plate.plate_index =='k/l':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='m/n')
        new_plate.save()
    elif last_plate.plate_index =='m/n':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='o/p')
        new_plate.save()   
    elif last_plate.plate_index =='q/r':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='s/t')
        new_plate.save() 
    elif last_plate.plate_index =='s/t':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='u/v')
        new_plate.save() 
    elif last_plate.plate_index =='u/v':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='w/x')
        new_plate.save() 
    elif last_plate.plate_index =='w/x':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='y/z')
        new_plate.save() 
    plates = VinylPlate.objects.filter(related_release=vinyl_release)
    plate_count = len(plates)
    vinyl_release.plate_count = plate_count
    vinyl_release.save
    pre_context['new_plate'] = new_plate
    return pre_context

def release_plate_add_submission(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    vinyl_release = VinylRelease.objects.get(id=release_id)
    current_plates = VinylPlate.objects.filter(related_release=vinyl_release)
    last_plate = []
    if len(current_plates) == 0:
        last_plate = None
    else:
        last_plate = current_plates.last()
    if last_plate == None:
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='a/b')
        new_plate.save()
    elif last_plate.plate_index =='a/b':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='c/d')
        new_plate.save()
    elif last_plate.plate_index =='c/d':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='e/f')
        new_plate.save()
    elif last_plate.plate_index =='e/f':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='g/h')
        new_plate.save()
    elif last_plate.plate_index =='g/h':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='i/j')
        new_plate.save()        
    elif last_plate.plate_index =='i/j':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='k/l')
        new_plate.save()                
    elif last_plate.plate_index =='k/l':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='m/n')
        new_plate.save()
    elif last_plate.plate_index =='m/n':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='o/p')
        new_plate.save()   
    elif last_plate.plate_index =='q/r':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='s/t')
        new_plate.save() 
    elif last_plate.plate_index =='s/t':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='u/v')
        new_plate.save() 
    elif last_plate.plate_index =='u/v':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='w/x')
        new_plate.save() 
    elif last_plate.plate_index =='w/x':
        new_plate = VinylPlate(related_release=vinyl_release, plate_index='y/z')
        new_plate.save() 
    plates = VinylPlate.objects.filter(related_release=vinyl_release)
    plate_count = len(plates)
    vinyl_release.plate_count = plate_count
    vinyl_release.save
    release = vinyl_release
    context = {
        'library': library,
        'release': release
    }
    return render(request, 'return_to_release_compile.html', context)

def release_plate_delete(request, library_id, release_id, plate_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    plate = VinylPlate.objects.get(id=plate_id)
    
    context = {
        'library': library,
        'release': release,
        'plate': plate
    }
    return render(request,'release_plate_delete.html', context)

def release_plate_delete_submission(request, library_id, release_id, plate_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    plate = VinylPlate.objects.get(id=plate_id)
    plate.delete()
    
    context = {
        'library': library,
        'release': release,
    }
    return render(request,'return_to_release_compile.html', context)

def return_to_release_compile(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    vinyl_release_average_tracks_per_side_util(release)
    context = {
        'library': library,
        'release': release,
    }
    return render(request, 'return_to_release_compile.html', context)

#endregion

#region track

def return_to_track_add(request, library_id, release_id, plate_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    plate = VinylPlate.objects.get(id=plate_id)
    context = {
        'library': library,
        'release': release,
        'plate': plate
    }
    return render(request,'return_to_track_add.html', context)

def return_to_track_categorize_next(request, library_id, release_id, index_count):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)

    context = {
        'library': library,
        'release': release,
        'index_count': index_count,
    }
    return render(request,'return_to_track_categorize_next.html', context)

def track_add(request, library_id, release_id, plate_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    plate = VinylPlate.objects.get(id=plate_id)
    context = {
        'library': library,
        'release': release,
        'plate': plate
    }
    return render(request,'track_add.html', context)

def track_add_go_to_first_track_add(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    plate = VinylPlate.objects.filter(related_release=release).first()
    context = {
        'library': library,
        'release': release,
        'plate': plate
    }
    return render(request,'track_add_go_to_first_track_add.html', context)

def track_add_submission(request, library_id, release_id, plate_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    if request.method == 'POST' and 'FILES':
        if 'next_plate' in request.POST and request.POST['index'] == '' and request.POST['title'] == '':
            plate = VinylPlate.objects.get(id=plate_id)
            if plate.plate_index == 'a/b':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='c/d')
            if plate.plate_index == 'c/d':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='e/f')
            if plate.plate_index == 'e/f':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='g/h')
            if plate.plate_index == 'g/h':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='i/j')
            if plate.plate_index == 'i/j':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='k/l')
            if plate.plate_index == 'k/l':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='m/n')
            if plate.plate_index == 'm/n':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='o/p')
            if plate.plate_index == 'o/p':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='q/r')
            if plate.plate_index == 'q/r':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='s/t')
            if plate.plate_index == 's/t':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='u/v')
            if plate.plate_index == 'u/v':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='w/x')
            if plate.plate_index == 'w/x':
                plater = VinylPlate.objects.filter(related_release=release).get(plate_index='y/z')
            plate = plater

            context = {
                'library': library,
                'release': release,
                'plate': plate
            }
            return render(request,'return_to_track_add.html', context)
        else:
            artist = str(request.POST['artist']).strip().replace(
                'Dj', 'DJ').replace(
                'dj', 'DJ').replace(
                'V/A', 'Various Artists').replace(
                'Various', 'Various Artists').replace(
                'Various Artists Artists', 'Various Artists').replace(
                'Feat', 'feat').replace(
                'Feat', 'feat').replace(
                'FEAT', 'feat').replace(
                'ft', 'feat')
            
            title = " ".join([word.title() if word not in "EP VIP DJ a" else word for word in str(request.POST['title']).split(" ")]).strip()
            title = title.replace(
                'vip', 'VIP').replace(
                'Vip', 'VIP').replace(
                'rmx', 'Remix').replace(
                'RMX', 'Remix').replace(
                'Rmx', 'Remix')
            remixer = str(request.POST['remixer']).title().strip()
            index = str(request.POST['index']).lower()
            bpm = request.POST['bpm']
            audio = request.FILES.get('audio')
            ## add crate_id field
            vinyl_track = VinylTrack(
                related_vinyl_plate_id=plate_id,
                artist=artist, 
                title=title,
                remixer=remixer, 
                index=index,
                audio=audio)
            vinyl_track.save()
            if bpm != '':
                vinyl_track.bpm = bpm
                vinyl_track.save()
            
            if 'same_plate' in request.POST:
                plate = VinylPlate.objects.get(id=plate_id)
                context = {
                    'library': library,
                    'release': release,
                    'plate': plate
                }
                return render(request,'return_to_track_add.html', context)
            
            elif 'next_plate' in request.POST:
                plate = VinylPlate.objects.get(id=plate_id)
                if plate.plate_index == 'a/b':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='c/d')
                if plate.plate_index == 'c/d':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='e/f')
                if plate.plate_index == 'e/f':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='g/h')
                if plate.plate_index == 'g/h':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='i/j')
                if plate.plate_index == 'i/j':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='k/l')
                if plate.plate_index == 'k/l':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='m/n')
                if plate.plate_index == 'm/n':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='o/p')
                if plate.plate_index == 'o/p':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='q/r')
                if plate.plate_index == 'q/r':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='s/t')
                if plate.plate_index == 's/t':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='u/v')
                if plate.plate_index == 'u/v':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='w/x')
                if plate.plate_index == 'w/x':
                    plater = VinylPlate.objects.filter(related_release=release).get(plate_index='y/z')
                plate = plater

                context = {
                    'library': library,
                    'release': release,
                    'plate': plate
                }
                return render(request,'return_to_track_add.html', context)
            
            
            elif 'finished_adding' in request.POST:
                plate = VinylPlate.objects.get(id=plate_id)
                context = {
                    'library': library,
                    'release': release,
                    'plate': plate
                }
                return render(request, 'return_to_release_compile.html', context)
    return redirect('/')

def track_audio_add(request, library_id, release_id, track_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    track = VinylTrack.objects.get(id=track_id)
    context = {
        'library': library,
        'release': release,
        'track': track
    }
    return render(request,'track_audio_add.html', context)

def track_audio_add_submission(request, library_id, release_id, track_id):
    library = Library.objects.get(id=library_id)
    if request.method == 'POST' and 'FILES':
        track = VinylTrack.objects.get(id=track_id)
        track.audio = request.FILES.get('audio')
        track.save()
        release = VinylRelease.objects.get(id=release_id)
        context = {
            'library': library,
            'release': release,
            'track': track
        }
        return render(request, 'return_to_release_compile.html', context)
    return redirect('/')

def track_categorize_first(request, library_id, release_id, track_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    track = VinylTrack.objects.get(id=track_id)
    genres = Genre.objects.all()
    vibe = Vibe.objects.all()
    energy_level = EnergyLevel.objects.all()
    index_count = 0
    context = {
        'library': library,
        'release': release,
        'track': track,
        'index_count': index_count,
        'genres': genres,
        'energy_level': energy_level,
        'vibe': vibe
    }
    return render(request,'track_categorize_first.html', context)

def track_categorize_next(request, library_id, release_id, index_count):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    genres = Genre.objects.all()
    vibe = Vibe.objects.all()
    energy_level = EnergyLevel.objects.all()
    track = VinylTrack.objects.filter(related_vinyl_plate__related_release=release)[index_count]
    context = {
        'library': library,
        'release': release,
        'track': track,
        'index_count': index_count,
        'genres': genres,
        'energy_level': energy_level,
        'vibe': vibe,
    }
    return render(request,'track_categorize_next.html', context)

def track_categorize_submission(request, library_id, release_id, track_id, index_count):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    track = VinylTrack.objects.get(id=track_id)
    tracks_length = len(VinylTrack.objects.filter(related_vinyl_plate__related_release=release))
    
    if request.method == 'POST':
        track.genre = request.POST['genre']
        track.vibe = request.POST['vibe']
        track.energy_level = request.POST['energy_level']
        track.save()
    if request.POST['master_genre_id'] != 'Choose...':
        release.master_genre = Genre.objects.get(id=request.POST['master_genre_id'])
        release.save()
    index_count += 1
    
    context = {
        'library': library,
        'release': release,
        'track': track,
        'index_count': index_count,
    }

    if index_count >= tracks_length:
        if release.on_previous_weekly_release_sheet == False:
            context['vinyl_release'] = release
            return render(request, 'return_to_stock_item_add_edit.html', context)
        else:
            return render(request, 'return_to_release_compile.html', context)
    
    else:
        track = VinylTrack.objects.filter(related_vinyl_plate__related_release=release)[index_count]
        return render(request,'return_to_track_categorize_next.html', context)

def track_delete(request, library_id, release_id, track_id):
    library = Library.objects.get(id=library_id)
    track = VinylTrack.objects.get(id=track_id)
    release = VinylRelease.objects.get(id=release_id)

    context = {
        'library': library,
        'release': release,
        'track': track
    }
    return render(request,'track_delete.html', context)

def track_delete_submission(request, library_id, release_id, track_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    track = VinylTrack.objects.get(id=track_id)

    track.delete()
    
    context = {
        'library': library,
        'release': release,
    }
    return render(request,'return_to_release_compile.html', context)

def track_edit(request, library_id, release_id, track_id,):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    track = VinylTrack.objects.get(id=track_id)
    plates = VinylPlate.objects.filter(related_release=release)
    index = VinylIndex.objects.all()

    context = {
        'library': library,
        'release': release,
        'track': track,
        'plates': plates,
        'index': index
    }
    return render(request,'track_edit.html', context)

def track_edit_submission(request, library_id, release_id, track_id,):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    track = VinylTrack.objects.get(id=track_id)

    if request.method == 'POST':
        track.artist = request.POST['artist']
        track.title = str(request.POST['title']).replace(
                'vip', 'VIP').replace(
                'Vip', 'VIP').replace(
                'rmx', 'Remix').replace(
                'RMX', 'Remix').replace(
                'Rmx', 'Remix')
        track.index = request.POST['index']
        track.remixer = request.POST['remixer']
        track.save()
        if request.POST['bpm'] and request.POST['bpm'] != '':
            track.bpm = request.POST['bpm']
            track.save()
        if request.POST['vinyl_plate_id'] != 'add_plate':
            vp = VinylPlate.objects.get(id=request.POST['vinyl_plate_id'])
            track.related_vinyl_plate = vp
            track.save()
        else:
            pre_context = {}
            release_plate_add_function(release_id, pre_context)
            track.related_vinyl_plate = pre_context['new_plate']
            track.save()

        context = {
            'library': library,
            'release': release,
            'track': track
        }
        return render(request, 'return_to_release_compile.html', context)
    return redirect('/')

#endregion


#region OLD
''' add bulk & release finalized
# release add bulk submission
def release_add_bulk_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    vinyl_releases_catalog_numbers = VinylRelease.objects.all().values_list('catalog_number', flat=True)

    file = open("static/musicDatabase/bulkUploads/bulk upload 2023 04 19.csv")
    csvreader = csv.reader(file)
    rows = []
    for row in csvreader:
       rows.append(row)

    for i in rows:
        if i[2] not in vinyl_releases_catalog_numbers and i[2] != '':
            release = VinylRelease(
                artist = i[0], 
                release_title = i[1],
                catalog_number = i[2],
                label = i[3],
                cost_price = Decimal(i[4]),
                stock_estimation = i[5],
                is_repress = i[6],
                supplier_id = i[7],
                plate_size = i[8],
                plate_count = i[9],
                vinyl_colour = i[10],
                release_type = i[11],
                sleeve_type = i[12],
                country = i[13],
                finalized = False,
                )
            release.save()

            if Decimal(i[9]) >= 1:
                plate_index = 'a/b'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 2:
                plate_index = 'c/d'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 3:
                plate_index = 'e/f'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 4:
                plate_index = 'g/h'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 5:
                plate_index = 'i/j'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 6:
                plate_index = 'k/l'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 7:
                plate_index = 'm/n'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 8:
                plate_index = 'o/p'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 9:
                plate_index = 'q/r'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 10:
                plate_index = 's/t'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 11:
                plate_index = 'u/v'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 12:
                plate_index = 'w/x'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()
            if Decimal(i[9]) >= 13:
                plate_index = 'y/z'
                obj = VinylPlate(
                    related_release=release, plate_index=plate_index)
                obj.save()

    context = {
        'library': library,
    }
    return render(request, 'return_to_vinyl_shop.html', context)

#release_finalized_submission
def release_finalized_submission(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    release.finalized = True
    release.save()

    context = {
        'library': library,
        'release': release,
    }
    return render(request,'return_to_release_compile.html', context)

'''
''' release database
#region release database
# release database
def release_database(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    _releases = VinylRelease.objects.all()

    track_crate_ids = _releases.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)
    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)

    #region create small artwork
    for r in _releases:
        if r.artwork:
            _, ext = os.path.splitext(r.artwork.path)
            image = Image.open(r.artwork.path)
            source_image = image.convert('RGB')
            source_image.thumbnail((100, 100))
            output = BytesIO()
            source_image.save(output, format='JPEG')
            output.seek(0)
            content_file = ContentFile(output.read())
            file = File(content_file)
            name = f'{uuid4()}{ext}'
            r.artwork_small.save(name, file, save=True)

    #endregion

    p = Paginator(_releases, 50)
    page = request.GET.get('page')
    releases = p.get_page(page)
    nums = "a" * releases.paginator.num_pages



    current_url = resolve(request.path_info).url_name
    member = Member.objects.get(id=member_id)
    member_want_list = MemberWantlist.objects.get(member=member)
    members_collection = LibraryPlate.objects.filter(contributor=member).values_list('related_vinyl_plate__related_release__id', flat=True)

    context = {
        'releases': releases,
        'library': library,
        'previous_url': current_url,
        'member_want_list': member_want_list,
        'members_collection': members_collection,
        
        'track_crate_ids': track_crate_ids,
        'nums': nums,
    }
    return render(request,'release_database.html', context)

# return to release database
def return_to_release_database(request, library_id):
    library = Library.objects.get(id=library_id)
    
    context = {
        'library': library,
    }
    return render(request,'return_to_release_database.html', context)

# release database search
def release_database_search(request, library_id):
    _releases = VinylRelease.objects.all()
    library = Library.objects.get(id=library_id)

    track_crate_ids = _releases.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
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
    search_release_year = request.POST['search_release_year']

    if search_track_crate_id != 'Catergory...':
        _releases = _releases.filter(related_vinyl_plate__related_vinyl_track__crate_id__exact=(search_track_crate_id)).distinct().order_by('-release_date')
    if search_artist:
        _releases = _releases.filter(related_vinyl_plate__related_vinyl_track__artist__icontains=(search_artist)).distinct().order_by('-release_date')   
    if search_label:
        _releases = _releases.filter(label__icontains=(search_label)).order_by('-release_date')
    if search_catalog:
        _releases = _releases.filter(catalog_number__icontains=(search_catalog)).order_by('-release_date')
    if search_release_year != '':
        _releases = _releases.filter(release_date__icontains=(search_release_year)).order_by('-release_date')

    track_crate_ids = _releases.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)
    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)
        
    p = Paginator(_releases, 500)
    page = request.GET.get('page')
    releases = p.get_page(page)
    nums = "a" * releases.paginator.num_pages

    current_url = resolve(request.path_info).url_name

    context = {
        'releases': releases,
        'library': library,

        'track_crate_ids': track_crate_ids,

        'search_track_crate_id': search_track_crate_id,
        'search_artist': search_artist,
        'search_label': search_label,
        'search_catalog': search_catalog,
        'search_release_year': search_release_year,

        'nums': nums,

        'previous_url': current_url,
    }

    return render(request,'release_database.html', context)

#endregion
'''
''' artist naming conventions
#region artist naming convention ##############
# artist naming convention
def artist_naming_conventions(request, library_id):
    library = Library.objects.get(id=library_id)
    artists = ArtistWrittenAs.objects.all()
    context = {
        'library': library,
        'artists': artists,
    }
    return render(request,'artist_naming_conventions.html', context)

# return to artist naming convention
def return_to_artist_naming_conventions(request, library_id):
    library = Library.objects.get(id=library_id)
    context = {
        'library': library,
    }
    return render(request, 'return_to_artist_naming_conventions.html', context)

# artist naming convention add
def artist_naming_convention_add(request, library_id):
    library = Library.objects.get(id=library_id)
    context = {
        'library': library,
    }
    return render(request,'artist_naming_convention_add.html', context)

# artist naming convention add submission
def artist_naming_convention_add_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    if request.method == 'POST':
        real_name = request.POST['real_name']
        use_this_artist_name = request.POST['use_this_artist_name']
        aliases = request.POST['aliases']
        obj = ArtistWrittenAs(
            real_name=real_name, use_this_artist_name=use_this_artist_name, 
            aliases=aliases)
        obj.save()

    artists = ArtistWrittenAs.objects.all()

    context = {
        'library': library,
        'artists': artists,
    }
    return render(request,'return_to_artist_naming_conventions.html', context)

# artist naming convention delete
def artist_naming_convention_delete(request, library_id, artist_written_as_id):
    library = Library.objects.get(id=library_id)
    artist = ArtistWrittenAs.objects.get(id=artist_written_as_id)
    context = {
        'library': library,
        'artist': artist
    }
    return render(request,'artist_naming_convention_delete.html', context)

# artist naming convention delete submission
def artist_naming_convention_delete_submission(request, library_id, artist_written_as_id):
    library = Library.objects.get(id=library_id)
    artists = ArtistWrittenAs.objects.all()

    if request.method == 'POST':
        artist = ArtistWrittenAs.objects.get(id=artist_written_as_id)
        artist.delete()
    
    context = {
        'library': library,
        'artists': artists,
    }
    return render(request,'return_to_artist_naming_conventions.html', context)

# artist naming convention edit
def artist_naming_convention_edit(request, library_id, artist_written_as_id):
    library = Library.objects.get(id=library_id)
    artist = ArtistWrittenAs.objects.get(id=artist_written_as_id)
    context = {
        'library': library,
        'artist': artist
    }
    return render(request,'artist_naming_convention_edit.html', context)

# artist naming convention edit submission
def artist_naming_convention_edit_submission(request, library_id, artist_written_as_id):
    library = Library.objects.get(id=library_id)
    if request.method == 'POST':
        artist = ArtistWrittenAs.objects.get(id=artist_written_as_id)
        artist.real_name = request.POST['real_name']
        artist.use_this_artist_name = request.POST['use_this_artist_name']
        artist.aliases = request.POST['aliases']
        artist.save()

        artists = ArtistWrittenAs.objects.all()
        context = {
            'library': library,
            'artists': artists,
        }
        return render(request,'return_to_artist_naming_conventions.html', context)
    return redirect('/')

# artist naming conventions search
def artist_naming_conventions_search(request, library_id):
    library = Library.objects.get(id=library_id)
    search_name = request.POST['search_name']
    artists = ArtistWrittenAs.objects.all().filter(
        real_name__icontains=(search_name)) | ArtistWrittenAs.objects.all().filter(
        use_this_artist_name__icontains=(search_name)) | ArtistWrittenAs.objects.all(
        ).filter(aliases__icontains=(search_name))
    context = {
        'library': library,
        'artists': artists
    }
    return render(request,'artist_naming_conventions.html', context)
#endregion
'''
''' unused
# release plate and  submission
def release_plate_and_track_count_submission(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    release = VinylRelease.objects.get(id=release_id)
    vinyl_plates = VinylPlate.objects.filter(related_release=release)
    _plate_count = len(vinyl_plates)
    _vinyl_tracks = []
    for i in vinyl_plates:
        vinyl_tracks = VinylTrack.objects.filter(related_vinyl_plate=i)
        for j in vinyl_tracks:
            _vinyl_tracks.append(j)

    _track_count = len(_vinyl_tracks)

    release.plate_count = _plate_count
    release.track_count = _track_count

    release.save()

    context = {
        'library': library,
        'release': release
    }
    return render(request, 'return_to_release_compile.html', context)
'''
#endregion