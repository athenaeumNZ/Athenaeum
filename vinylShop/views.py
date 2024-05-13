from django.shortcuts import render
from datetime import datetime, timedelta, date
import csv
import urllib.parse
from django.urls import resolve
from accounts.models import OrderRequestItem
from accounts.utils import make_email_list
from cart.cart import Cart
from choices.models import Genre
from management.models import EnergyLevel, Library, Vibe, VinylDistributor, Member
from members.utils import member_recommendations_based_on_member_releases
from musicDatabase.models import VinylPlate, VinylRelease, VinylTrack
from shoppingCart.shopping_cart import ShoppingCart
from vinylLibrary.models import LibraryPlate
from vinylShop.models import ShopGenre, StockItem, WeeklyReleaseSheet
from .utils import convert_stock_items_to_vinyl_releases_util, update_not_black_util, update_stock_items_vinyl_releases_not_black_util
from musicDatabase.utils import vinyl_release_average_tracks_per_side_util, vinyl_releases_average_tracks_per_side_util
from django.urls import reverse

from django_xhtml2pdf.utils import pdf_decorator

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.template.loader import render_to_string
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

def print_crate_divider_stockpile(request, library_id, member_id): # Probably in the wrong place
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    context = {
        'library': library,
        'member': member,
    }
    return render(request, 'print_crate_divider_stockpile.html', context)


''' REDUNDANT ->'''
def personal_weekly_releases(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    search_start_date = request.POST['search_start_date']
    search_end_date = request.POST['search_end_date']
    member = Member.objects.get(id=member_id)
    
    #region ################# Preferences WILL BE REMOVED AND DYNAMICALLY CREATED
    prefered_genres = Member.objects.filter(id=member_id).values_list('prefered_genres__genre', flat=True).order_by('prefered_genres__genre')
    prefered_vibes = Member.objects.filter(id=member_id).values_list('prefered_vibes__vibe', flat=True)
    prefered_energy_levels = Member.objects.filter(id=member_id).values_list('prefered_energy_level__energy_level', flat=True)

    prefered_crate_ids = []
    for g in prefered_genres:
        prefered_crate_ids.append( str(g))
        for v in prefered_vibes:
            for e in prefered_energy_levels:
                prefered_crate_ids.append( str(g) + ' ' + str(v[:1]) + str(e) )

    irrelevant_genres = Member.objects.filter(id=member_id).values_list('irrelevant_genres__genre', flat=True)
    irrelevant_vibes = Member.objects.filter(id=member_id).values_list('irrelevant_vibes__vibe', flat=True)
    irrelevant_energy_levels = Member.objects.filter(id=member_id).values_list('irrelevant_energy_level__energy_level', flat=True)

    irrelevant_crate_ids = []

    for g in irrelevant_genres:
        for v in irrelevant_vibes:
            for e in irrelevant_energy_levels:
                irrelevant_crate_ids.append( str(g) + ' ' + str(v[:1]) + str(e) )

    for v in irrelevant_vibes:
        for e in irrelevant_energy_levels:
            irrelevant_crate_ids.append( str(v[:1]) + str(e) )

    for e in irrelevant_energy_levels:
        irrelevant_crate_ids.append(str(e))

    genres = Genre.objects.all().order_by('genre')
    for i in genres:
        for j in irrelevant_genres:
            if str(i.genre) == str(j):
                genres = genres.exclude(id=i.pk)

    for i in genres:
        for j in prefered_genres:
            if str(i.genre) == str(j):
                genres = genres.exclude(id=i.pk)

    #endregion

    #region ################# releases
    _releases = VinylRelease.objects.filter(
        release_date__gte=search_start_date).filter(
        release_date__lte=search_end_date).filter(
        stock_estimation__gte=1).exclude(distributor__distributor_code__exact='UES')
    # filter out irrelevant releases
    releases = []
    for r in _releases:
        for c in r.crate_id:
            if c not in irrelevant_crate_ids:
                if r not in releases:
                    releases.append(r)
    # releases to check out
    for r in releases:
        for c in r.crate_id:
            if c in prefered_crate_ids:
                r.release_to_check_out = True

    #endregion

    #region ################# Forthcoming
    _pre_orders = VinylRelease.objects.filter(
        release_date__gt=search_end_date).filter(
        stock_estimation__gte=1).order_by('release_date')
        
    # filter out irrelevant releases
    pre_orders = []
    for r in _pre_orders:
        for c in r.crate_id:
            if c not in irrelevant_crate_ids:
                if r not in pre_orders:
                    pre_orders.append(r)

    # releases to check out
    for r in pre_orders:
        for c in r.crate_id:
            if c in prefered_crate_ids:
                r.release_to_check_out = True            
    #endregion

    #region ################# Past releases that have just added to the database this week
    _previously_not_availible_releases = VinylRelease.objects.filter(
        release_date__lt=search_start_date).filter(
        stock_estimation__gte=1).filter(
        on_previous_weekly_release_sheet=False)


    # # filter out irrelevant releases
    previously_not_availible_releases = []
    for r in _previously_not_availible_releases:
        for c in r.crate_id:
            if c not in irrelevant_crate_ids:
                if r not in previously_not_availible_releases:
                    previously_not_availible_releases.append(r)

    # releases to check out
    for r in previously_not_availible_releases:
        for c in r.crate_id:
            if c in prefered_crate_ids:
                r.release_to_check_out = True
    #endregion
    
    context = {
        'prefered_genres': prefered_genres,
        'prefered_vibes': prefered_vibes,
        'prefered_energy_levels': prefered_energy_levels,
        'irrelevant_genres': irrelevant_genres,
        'genres': genres,
        'prefered_crate_ids': prefered_crate_ids,
        'irrelevant_crate_ids': irrelevant_crate_ids,
        'member': member,
        'library': library,
        'releases': releases,
        'pre_orders': pre_orders,
        'search_start_date': search_start_date,
        'search_end_date': search_end_date,
        'previously_not_availible_releases': previously_not_availible_releases,
    }
    
    return render(request, 'personal_weekly_releases.html', context)

#endregion

#region vinyl ordering. This is becoming pretty redundant

def return_to_vinyl_ordering(request, library_id):
    library = Library.objects.get(id=library_id)

    context = {
        'library': library
    }
    return render(request,'return_to_vinyl_ordering.html', context)

def vinyl_ordering(request, library_id):
    library = Library.objects.get(id=library_id)
    members = Member.objects.filter(
        library=library).filter(
        active=True)
    current_url = resolve(request.path_info).url_name
    cart = Cart(request)
    items = cart.items_list

    vinyl_releases = VinylRelease.objects.all().order_by('catalog_number')[:0]

    #region query_order_by
    query_order_by = [
        'Stock Estimation',
        'Most Recent',
        'Oldest',
        'Catalog Number',
    ]
    #endregion

    #region query filter
    query_filter = [
        'Want List',
        'In Stock',
        'Wantlist & In Stock',
        'Low Stock',
        'Want List & Low Stock',
        'Not Finalized',
        'Not W M or U',
        'Check Availability'
    ]
    #endregion

    distributors = VinylDistributor.objects.all()
  
    context = {
        'vinyl_releases': vinyl_releases,
        'library':library,
        'members': members,
        'cart': cart,
        'items': items,
        'previous_url': current_url,
        'distributors': distributors,
        'query_order_by': query_order_by,
        'query_filter': query_filter,
    }
    return render(request,'vinyl_ordering.html', context)

def vinyl_ordering_search(request, library_id):
    library = Library.objects.get(id=library_id)
    distributors = VinylDistributor.objects.all()
    current_url = resolve(request.path_info).url_name

    members = Member.objects.filter(
        library=library).filter(
        active=True)
    
    cart = Cart(request)
    items = cart.items_list

    vinyl_releases = VinylRelease.objects.all()

    search_stock_levels = '0'
    
    #region search fields
    search_artist = request.POST['search_artist']
    search_label = request.POST['search_label']
    search_catalog = request.POST['search_catalog']
    search_distributor = request.POST['search_distributor']
    search_order_by = request.POST['search_order_by']
    search_query_filter = request.POST['search_query_filter']

    if search_artist != 'Artist...' and search_artist != None:
        vinyl_releases = vinyl_releases.filter(related_vinyl_plate__related_vinyl_track__artist__icontains=(search_artist)).distinct().order_by('stock_estimation', '-release_date')   
    if search_label != 'Label...' and search_label != None:
        vinyl_releases = vinyl_releases.filter(label__icontains=(search_label)).order_by('stock_estimation', '-release_date')
    if search_catalog != 'Catalog...' and search_catalog != None:
        vinyl_releases = vinyl_releases.filter(catalog_number__icontains=(search_catalog)).order_by('stock_estimation', '-release_date')
    if search_distributor != 'Dist...' and search_distributor != None:
        vinyl_releases = vinyl_releases.filter(supplier__distributor_code__icontains=(search_distributor)).order_by('stock_estimation', '-release_date')
    #endregion

    #region query order by

    query_order_by = [
        'Stock Estimation',
        'Most Recent',
        'Oldest',
        'Catalog Number',
    ]
        
    if search_order_by == 'Stock Estimation':
        vinyl_releases = vinyl_releases.order_by('stock_estimation')
    elif search_order_by == 'Most Recent':
        vinyl_releases = vinyl_releases.order_by('-release_date')
    elif search_order_by == 'Oldest':
        vinyl_releases = vinyl_releases.order_by('release_date')
    elif search_order_by == 'Catalog Number':
        vinyl_releases = vinyl_releases.order_by('catalog_number')
    else:
        vinyl_releases = vinyl_releases.order_by('catalog_number')
    #endregion

    #region query filter

    query_filter = [
        'Want List',
        'In Stock',
        'Wantlist & In Stock',
        'Low Stock',
        'Want List & Low Stock',
        'Not Finalized',
        'Not W M or U',
        'Check Availability',
    ]

    if search_query_filter == 'In Stock':
        vrs = []
        mcs = LibraryPlate.objects.filter(contributor=member)
        for i in vinyl_releases:
            for j in mcs:
                if i == j.related_vinyl_plate.related_release and i not in vrs:
                    vrs.append(i)
        vinyl_releases = vrs

    elif search_query_filter == 'Want List':
        mwl= MemberWantlist.objects.filter(member=member).values_list('want_list', flat=True)
        vrs = []
        for i in vinyl_releases:
            for j in mwl:
                if i.id == j and i not in vrs:
                    vrs.append(i)
        vinyl_releases = vrs
    

    elif search_query_filter == 'Wantlist & In Stock':
        mwl= MemberWantlist.objects.filter(member=member).values_list('want_list', flat=True)
        mcs = LibraryPlate.objects.filter(contributor=member)
        vrs = []
        for i in vinyl_releases:
            for j in mwl:
                for k in mcs:
                    if i.id == j and i == k.related_vinyl_plate.related_release and i not in vrs:
                        vrs.append(i)
        vinyl_releases = vrs

    elif search_query_filter == 'Low Stock':
        vinyl_releases = vinyl_releases.filter(stock_estimation__lte=10)

    elif search_query_filter == 'Want List & Low Stock':
        vinyl_releases = vinyl_releases.filter(stock_estimation__lte=10).order_by('-release_date')
        mwl= MemberWantlist.objects.filter(member=member).values_list('want_list', flat=True)
        vrs = []
        for i in vinyl_releases:
            for j in mwl:
                if i.id == j and i not in vrs:
                    vrs.append(i)
        vinyl_releases = vrs

    elif search_query_filter == 'Not W M or U':
        mwl= MemberWantlist.objects.filter(member=member).values_list('want_list', flat=True)
        muwl= MemberUnwantedList.objects.filter(member=member).values_list('unwanted_list', flat=True)
        mml = MemberMaybeList.objects.filter(member=member).values_list('maybe_list', flat=True)
        vrs = []
        for i in vinyl_releases:
            if i.pk not in mwl and i.pk not in muwl and i.pk not in mml:
                vrs.append(i)
        vinyl_releases = vrs

    elif search_query_filter == 'Not Finalized':
        vinyl_releases = VinylRelease.objects.filter(finalized=False).order_by('artwork')

    elif search_query_filter == 'Check Availability':
        vinyl_releases = vinyl_releases.filter(
            check_stock_availibility=True).filter(
            stock_estimation__gte=1)

    else:
        vinyl_releases = vinyl_releases
    #endregion

    
    #region in_stock
    current_member = request.user
    if current_member == library.library_shop:
        in_stock_items = StockItem.objects.filter(library=library)
        in_coming_stock = OrderRequestItem.objects.filter(
            order_request__member=current_member.member).filter(
            stockpiled=False)
        for i in vinyl_releases:
            for j in in_stock_items:
                if i == j.vinyl_release:
                    i.quantity_in_stock = j.quantity
            for k in in_coming_stock:
                if i == k.vinyl_release:
                    i.quantity_incoming_stock = k.quantity
    #endregion
    
    context = {
        'vinyl_releases': vinyl_releases,
        'library':library,
        'cart': cart,
        'items': items,
        'members': members,
        'search_artist': search_artist,
        'search_label': search_label,
        'search_catalog': search_catalog,
        'search_stock_levels': search_stock_levels,
        'search_distributor': search_distributor,
        'search_order_by': search_order_by,
        'search_query_filter': search_query_filter,
        'current_url': current_url,

        'previous_url': current_url,
        'distributors': distributors,
        'query_order_by': query_order_by,
        'query_filter': query_filter,
    }

    return render(request,'vinyl_ordering.html', context)

def update_distributors_stock_submission(request, library_id): # there needs to be a better way of doing this, some sort of API linking into the distributors stock levels.
    library = Library.objects.get(id=library_id)
    vinyl_releases = VinylRelease.objects.all()
    vinyl_distributors = VinylDistributor.objects.filter(auto_update=True)
    for i in vinyl_distributors:
        distributor_code = i.distributor_code
        file = open('static/vinylShop/updateDistributorsStock/' + str(distributor_code) + '.csv')
        if csv.reader(file):
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)

            rows_checked = []
            for k in rows:
                for j in vinyl_releases:
                    if k[0] == j.catalog_number and k not in rows_checked:
                        j.supplier = i
                        j.cost_price = k[1]
                        j.stock_estimation = k[2]
                        j.save()
                if i not in rows_checked:
                    rows_checked.append(k[0])
    
    context = {
        'library': library,
    }

    return render(request,'return_to_vinyl_ordering.html', context)

#endregion

#region weekly releases. Will need to be replaced by different templates / maybe a new release button on the vinyl shop page

def return_to_weekly_release_sheets(request, library_id):
    library = Library.objects.get(id=library_id)

    context = {
        'library': library,
    }
    return render(request, 'return_to_weekly_release_sheets.html', context)

def weekly_releases(request, library_id, weekly_release_sheet_id):
    library = Library.objects.get(id=library_id)
    weekly_release_sheet = WeeklyReleaseSheet.objects.get(id=weekly_release_sheet_id)  
    search_start_date = weekly_release_sheet.search_start_date
    search_end_date = weekly_release_sheet.search_end_date
    scroll_position = request.GET.get('scroll_position')
    #region this week
    
    def update_stock_items(releases):
        for release in releases:
            stock_items = StockItem.objects.filter(library=library, vinyl_release=release)
            if stock_items.exists():
                setattr(release, 'stock_item', stock_items.first())
            else:
                setattr(release, 'stock_item', None)

    #region Fetch releases within search date range with stock estimation
    releases = VinylRelease.objects.filter(
        release_date__gte=search_start_date,
        release_date__lte=search_end_date,
        stock_estimation__gte=1
    )

    # Update stock items for releases
    for release in releases:
        stock_items = StockItem.objects.filter(library=library, vinyl_release=release)
        if stock_items.exists():
            setattr(release, 'stock_item', stock_items.first())
        else:
            setattr(release, 'stock_item', None)
    #endregion
    #region Fetch forthcoming releases
    forthcoming_releases = VinylRelease.objects.filter(
        release_date__gt=search_end_date,
        stock_estimation__gte=1
    ).exclude(distributor__distributor_code__exact='UES')

    # Update stock items for forthcoming releases
    for release in forthcoming_releases:
        stock_items = StockItem.objects.filter(library=library, vinyl_release=release)
        if stock_items.exists():
            release.stock_item = stock_items.first()
        else:
            release.stock_item = None
    #endregion
    #region Fetch back catalog releases
    back_catalog = VinylRelease.objects.filter(
        release_date__lt=search_start_date,
        stock_estimation__gte=1,
        on_previous_weekly_release_sheet=False
    ).exclude(distributor__distributor_code__icontains='UES')

    # Update stock items for back catalog releases
    for release in back_catalog:
        stock_items = StockItem.objects.filter(library=library, vinyl_release=release)
        if stock_items.exists():
            release.stock_item = stock_items.first()
        else:
            release.stock_item = None
    #endregion

    
    '''#region full_stock_list
    full_stock_items = StockItem.objects.filter(
        library=library,
        quantity_plus_quantity_incoming_stock__gte=1
        ).exclude(
            vinyl_release__in=forthcoming_releases or releases or back_catalog)
    full_stock_list = []
    for i in full_stock_items:
        full_stock_list.append(i.vinyl_release)
    vinyl_releases_contained = VinylRelease.objects.filter(catalog_number__in=full_stock_list)
    full_stock_list = vinyl_releases_contained.order_by('most_common')
    for r in full_stock_list:
        stock_items = StockItem.objects.filter(library=library, vinyl_release=r)
        if len(stock_items) >= 1:
            stock_item = stock_items.first()
        else:
            stock_item = None
        r.stock_item = stock_item
    #endregion 'full_stock_list': full_stock_list, '''

    '''#region member_recommended
    member = Member.objects.get(user__first_name__icontains='Angus')
    member_recommended = member_recommendations_based_on_member_releases(member.pk, library_id)
    full_member_recommended_list = []
    for i in member_recommended:
        full_member_recommended_list.append(i.vinyl_release)
    vinyl_releases_contained = VinylRelease.objects.filter(catalog_number__in=full_member_recommended_list)
    full_member_recommended_list = vinyl_releases_contained.order_by('most_common')
    for r in full_member_recommended_list:
        stock_items = StockItem.objects.filter(library=library, vinyl_release=r)
        if len(stock_items) >= 1:
            stock_item = stock_items.first()
        else:
            stock_item = None
        r.stock_item = stock_item
                'full_member_recommended_list': full_member_recommended_list,
    #endregion'''
              
    ''' utils
    vinyl_releases_average_tracks_per_side_util(releases)
    vinyl_releases_average_tracks_per_side_util(forthcoming_releases)
    vinyl_releases_average_tracks_per_side_util(back_catalog)
    vinyl_releases_average_tracks_per_side_util(full_stock_list)
    '''
    
    context = {
        'library': library,
        'weekly_release_sheet': weekly_release_sheet,
        'releases': releases,
        'search_start_date': search_start_date,
        'search_end_date': search_end_date,
        'forthcoming_releases': forthcoming_releases,
        'back_catalog': back_catalog,
        'scroll_position': scroll_position,   
    }

    return render(request, 'weekly_releases.html', context)

def stock_item_add_edit_order_submission(request):
    scroll_position = request.POST.get('scroll_position')
    if request.method == "POST":
        library_id = request.POST.get('library_id')
        weekly_release_sheet_id = request.POST.get('weekly_release_sheet_id')
        library = Library.objects.get(pk=library_id)
        # Get the release ID and quantity from the request
        release_id = request.POST['release_id']

        try:
            # Check if the release already exists in stock
            stock_item = StockItem.objects.get(library=library, vinyl_release_id=release_id)
            stock_item.save()
            ordering_stock_item = stock_item
        except StockItem.DoesNotExist:
            # If not, create a new stock item
            release = VinylRelease.objects.get(id=release_id)
            new_stock_item = StockItem(
                library=library,
                vinyl_release=release,
                quantity=0,
                price=999,
                auto_restock_threshold=1,
                auto_restock_quantity=1,
                updated_by_library_shop=True
            )
            new_stock_item.save()
            ordering_stock_item = new_stock_item

        #region update genres list
        potential_genres = []
        release = VinylRelease.objects.get(id=release_id)
        item_plates = VinylPlate.objects.filter(related_release=release)
        item_tracks = VinylTrack.objects.filter(related_vinyl_plate__in=item_plates)
        for j in item_tracks:
            if j.genre not in potential_genres and j.genre != '-':
                potential_genres.append(j.genre)
        shop_genres = ShopGenre.objects.filter(library=library).values_list('genre')
        for i in potential_genres:
            if len(ShopGenre.objects.filter(library=library, genre__genre=i)) <= 0:
                this_genre = Genre.objects.filter(genre=i).first()
                new_genre = ShopGenre(
                    genre = this_genre,
                    library = library,
                )
                new_genre.save()
        #endregion
        #region order for shop
        if request.POST['quantity_to_order'] != '':
            librarian = Member.objects.get(user=library.library_shop)
            stock_item = ordering_stock_item
            vinyl_release = release
            order_request_item = OrderRequestItem(
                library = library,
                member = librarian,
                stock_item = stock_item,
                vinyl_release = vinyl_release,
                quantity = int(request.POST['quantity_to_order']),
                sale_price = 0,
                shop_purchase = False,
                to_become_shop_stock = True,
            )
            order_request_item.save()
            stock_item.quantity_incoming += int(request.POST['quantity_to_order'])
            stock_item.quantity_plus_quantity_incoming_stock += int(request.POST['quantity_to_order'])
            stock_item.save()        
            stock_estimation = VinylRelease.objects.filter(catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - int(request.POST['quantity_to_order'])
            if stock_estimation >= 0:
                vinyl_release = stock_item.vinyl_release
                vinyl_release.stock_estimation = stock_estimation
                vinyl_release.save()
            else:
                vinyl_release.stock_estimation = 0
                vinyl_release.save()
            stock_estimation = VinylRelease.objects.filter(catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0]
            if stock_estimation >= 0:
                vinyl_release = stock_item.vinyl_release
                vinyl_release.stock_estimation = stock_estimation
                vinyl_release.save()
                
        
        redirect_url = reverse('weekly_releases', args=[library_id, weekly_release_sheet_id])
        redirect_url += f'?scroll_position={scroll_position}'
        return HttpResponseRedirect(redirect_url)
    else:
        # Handle GET requests or invalid requests
        return HttpResponseBadRequest()

def weekly_releases_set_to_on_previous_release_sheet_submission(request, library_id, weekly_release_sheet_id, search_start_date, search_end_date):
    library = Library.objects.get(id=library_id)
    sheet = WeeklyReleaseSheet.objects.get(id=weekly_release_sheet_id)
    
    ################# releases #################
    releases = VinylRelease.objects.filter(
        release_date__gte=search_start_date).filter(
        release_date__lte=search_end_date).filter(
        stock_estimation__gte=1)

    # releases on this weeks sheet
    releases_on_this_weekly_release_sheet = []
    for r in releases:
        releases_on_this_weekly_release_sheet.append(r)

    
    ################# Forthcoming #################
    pre_orders = VinylRelease.objects.filter(
        release_date__gt=search_end_date).filter(
        stock_estimation__gte=1)
    
    for r in pre_orders:
        releases_on_this_weekly_release_sheet.append(r)

    ################# Past releases that have just added to the database this week #################
    previously_not_availible_releases = VinylRelease.objects.filter(
        release_date__lt=search_start_date).filter(
        stock_estimation__gte=1).filter(
        on_previous_weekly_release_sheet=False)

    for r in previously_not_availible_releases:
        releases_on_this_weekly_release_sheet.append(r)


    #region full_stock_list
        '''
    stock_items = StockItem.objects.filter(
        library=library,
        quantity_plus_quantity_incoming_stock__gte=1
        ).exclude(
            vinyl_release__in=previously_not_availible_releases or releases or pre_orders)
    full_stock_list = []
    for i in stock_items:
        full_stock_list.append(i.vinyl_release)
    vinyl_releases_contained = VinylRelease.objects.filter(catalog_number__in=full_stock_list)
    for r in vinyl_releases_contained:
        releases_on_this_weekly_release_sheet.append(r)
    '''
    #endregion
    # update the release status 
    for i in releases_on_this_weekly_release_sheet:
        release_ = VinylRelease.objects.get(catalog_number=i)
        release_.on_previous_weekly_release_sheet = True
        release_.back_in_stock = False
        release_.save()

    # update the sheet status
    sheet.release_sheet_finalized = True
    sheet.save()

    context = {
        'library': library,
        'search_start_date': search_start_date,
        'search_end_date': search_end_date

    }
    return render(request, 'return_to_weekly_release_sheets.html', context)

def weekly_release_sheet_add(request, library_id):
    library = Library.objects.get(id=library_id)

    context = {
        'library': library
    }
    return render(request, 'weekly_release_sheet_add.html', context)

def weekly_release_sheet_add_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    
    if request.method == 'POST':
        search_start_date = request.POST['search_start_date']
        search_end_date = request.POST['search_end_date']
        sheet = WeeklyReleaseSheet(
            search_start_date=search_start_date, search_end_date=search_end_date)
        sheet.save()

    context = {
        'library': library
    }

    return render(request, 'return_to_weekly_release_sheets.html', context)

def weekly_release_sheet_edit(request, library_id, weekly_release_sheet_id):
    library = Library.objects.get(id=library_id)
    weekly_release_sheet = WeeklyReleaseSheet.objects.get(id=weekly_release_sheet_id)

    context = {
        'library': library,
        'weekly_release_sheet': weekly_release_sheet,
    }
    return render(request, 'weekly_release_sheet_edit.html', context)

def weekly_release_sheet_edit_submission(request, library_id, weekly_release_sheet_id):
    library = Library.objects.get(id=library_id)
    
    weekly_release_sheet = WeeklyReleaseSheet.objects.get(id=weekly_release_sheet_id)
    weekly_release_sheet.search_start_date = request.POST['search_start_date']
    weekly_release_sheet.search_end_date = request.POST['search_end_date']
    weekly_release_sheet.save()

    context = {
        'library': library
    }

    return render(request, 'return_to_weekly_release_sheets.html', context)

def weekly_release_sheet_upload(request, library_id, weekly_release_sheet_id):
    library = Library.objects.get(id=library_id)
    sheet = WeeklyReleaseSheet.objects.get(id=weekly_release_sheet_id)
    context = {
        'library': library,
        'sheet': sheet,
    }
    return render(request, 'weekly_release_sheet_upload.html', context)

def weekly_release_sheet_upload_submission(request, library_id, weekly_release_sheet_id):
    library = Library.objects.get(id=library_id)
    sheet = WeeklyReleaseSheet.objects.get(id=weekly_release_sheet_id)

    if request.method == 'POST' and 'FILES':
        sheet.printable_release_sheet = request.FILES.get('printable_release_sheet')
        sheet.save()

    context = {
        'library': library
    }

    return render(request, 'return_to_weekly_release_sheets.html', context)

def weekly_release_sheets(request, library_id):
    library = Library.objects.get(id=library_id)
    email_list = make_email_list(library)
    release_sheets = WeeklyReleaseSheet.objects.all()
    members = Member.objects.filter(
        library=library).exclude(
        membership_number='ASN001').filter(
        active=True)
    vibes = Vibe.objects.all()
    genres = Genre.objects.all()
    energy_levels = EnergyLevel.objects.all()

    context = {
        'library': library,
        'genres': genres,
        'vibes': vibes,
        'energy_levels': energy_levels,
        'release_sheets': release_sheets,
        'members': members,
        'email_list': email_list,
    }
    return render(request, 'weekly_release_sheets.html', context)

#endregion
'''<- <- REDUNDANT '''

#region vinyl shop

def return_to_stock_item_add_edit_select(request, library_id):
    library = Library.objects.get(id=library_id) 
    releases = VinylRelease.objects.all()[:0]

    context = {
        'library': library,
        'releases': releases,
    }
    return render(request, 'return_to_stock_item_add_edit_select.html', context)

def return_to_vinyl_shop(request, library_id):
    library = Library.objects.get(id=library_id)
    context = {
        'library':library,
    }
    return render(request,'return_to_vinyl_shop.html', context)

def stock_item_add_edit(request, library_id, release_id):
    library = Library.objects.get(id=library_id) 
    release = VinylRelease.objects.get(id=release_id)
    if len(StockItem.objects.filter(library=library).filter(vinyl_release=release)) >= 1:
        stock_item = StockItem.objects.filter(library=library).get(vinyl_release=release)
    else:
        stock_item = None

    other_stock_items_on_label = StockItem.objects.filter(
        library=library,
        vinyl_release__label=release.label).order_by(
            'vinyl_release__release_date',
        )
    plates = VinylPlate.objects.filter(related_release=release)
    tracks = VinylTrack.objects.filter(related_vinyl_plate__in=plates)
    shopping_cart = ShoppingCart(request)
    genres = Genre.objects.all()
    context = {
        'library': library,
        'genres': genres,
        'release': release,
        'stock_item': stock_item,
        'other_stock_items_on_label': other_stock_items_on_label,
        'tracks': tracks,
        'shopping_cart': shopping_cart,
    }
    if request.GET.get('search_start_date'):
        context['search_start_date'] = request.GET.get('search_start_date')
    if request.GET.get('search_end_date'):
        context['search_end_date'] = request.GET.get('search_end_date')
    if request.GET.get('scroll_position'):
        context['scroll_position'] = request.GET.get('scroll_position')
    return render(request, 'stock_item_add_edit.html', context)

def return_to_stock_item_add_edit(request, library_id, vinyl_release_id):
    library = Library.objects.get(id=library_id) 
    vinyl_release = VinylRelease.objects.get(id=vinyl_release_id)
    context = {
        'library': library,
        'vinyl_release': vinyl_release,
    }
    return render(request, 'return_to_stock_item_add_edit.html', context)

def stock_item_add_edit_select(request, library_id):
    library = Library.objects.get(id=library_id) 
    context = {
        'library': library,
    }
    return render(request, 'stock_item_add_edit_select.html', context)

def stock_item_add_edit_select_search(request, library_id):
    library = Library.objects.get(id=library_id) 
    releases = VinylRelease.objects.all() # .filter(distributor__active=True)
    stock_items_added_by_member = StockItem.objects.filter(
        library=library, added_by_member=True).values_list('vinyl_release__catalog_number', flat=True)
    stock_items_quantities = StockItem.objects.filter(
        library=library, quantity__gte=1).values_list('vinyl_release__catalog_number', flat=True)
    stock_items_quantities_incoming = StockItem.objects.filter(
        library=library, quantity_incoming__gte=1).values_list('vinyl_release__catalog_number', flat=True)
    stock_items = StockItem.objects.filter(
        library=library).values_list('vinyl_release__catalog_number', flat=True)

    #region search fields
    search_artist = request.POST['search_artist']
    search_title = request.POST['search_title']
    search_label = request.POST['search_label']
    search_catalog = request.POST['search_catalog']

    if search_artist != 'Artist...' and search_artist != None:
        releases = releases.filter(related_vinyl_plate__related_vinyl_track__artist__icontains=(search_artist)).distinct()
    
    if search_title != 'Title...' and search_title != None:
        releases = releases.filter(related_vinyl_plate__related_vinyl_track__title__icontains=(search_title)).distinct()
    
    if search_label != 'Label...' and search_label != None:
        releases = releases.filter(label__icontains=(search_label)).distinct()
    
    if search_catalog != 'Catalog...' and search_catalog != None:
        releases = releases.filter(catalog_number__icontains=(search_catalog)).distinct()

    releases.order_by('catalog_number')
    search_results_count = releases.count()
    #endregion

    context = {
        'library': library,
        'releases': releases,
        'search_artist': search_artist,
        'search_title': search_title,
        'search_label': search_label,
        'search_catalog': search_catalog,
        'search_results_count': search_results_count,
        'stock_items_quantities': stock_items_quantities,
        'stock_items_quantities_incoming': stock_items_quantities_incoming,
        'stock_items_added_by_member': stock_items_added_by_member,
        'stock_items': stock_items,
    }
    return render(request, 'stock_item_add_edit_select.html', context)

def stock_item_member_add_submission(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    new_stock_item = StockItem(
        library = library,
        vinyl_release = VinylRelease.objects.get(id=release_id),
        quantity = 0,
        price = 999,
        added_by_member = True,
    )
    new_stock_item.save()

    context = {
        'library': library,
    }

    return render(request, 'return_to_vinyl_shop.html', context)

def stock_item_add_edit_submission(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    current_stock_items = StockItem.objects.filter(library=library)
    current_stock_items_releases = current_stock_items.values_list("vinyl_release__catalog_number", flat=True)

    release = VinylRelease.objects.get(id=release_id)
    if release.catalog_number in current_stock_items_releases:
        stock_item = StockItem.objects.get(vinyl_release=release)
        if stock_item.quantity != None:
            stock_item.quantity += int(request.POST['quantity'])
        stock_item.price = request.POST['price']
        stock_item.auto_restock = request.POST['auto_restock']
        stock_item.auto_restock_threshold = request.POST['auto_restock_threshold']
        stock_item.auto_restock_quantity = request.POST['auto_restock_quantity']
        stock_item.updated_by_library_shop = True
        stock_item.in_library_shop_want_list = request.POST['in_library_shop_want_list']
        stock_item.save()
        ordering_stock_item = stock_item
    else:
        new_stock_item = StockItem(
            library=library,
            vinyl_release=release,
            quantity=request.POST['quantity'],
            price=request.POST['price'],
            updated_by_library_shop=True
        )
        new_stock_item.save()
        ordering_stock_item = new_stock_item

    #region update genres list
    potential_genres = []
    item_plates = VinylPlate.objects.filter(related_release=release)
    item_tracks = VinylTrack.objects.filter(related_vinyl_plate__in=item_plates)
    for j in item_tracks:
        if j.genre not in potential_genres and j.genre != '-':
            potential_genres.append(j.genre)
    shop_genres = ShopGenre.objects.filter(library=library).values_list('genre')
    for i in potential_genres:
        if len(ShopGenre.objects.filter(library=library, genre__genre=i)) <= 0:
            this_genre = Genre.objects.filter(genre=i).first()
            new_genre = ShopGenre(
                genre=this_genre,
                library=library,
            )
            new_genre.save()
    #endregion
    #region order for shop
    if request.POST['quantity_to_order'] != '':
        librarian = Member.objects.get(user=library.library_shop)
        stock_item = ordering_stock_item
        vinyl_release = release
        order_request_item = OrderRequestItem(
            library=library,
            member=librarian,
            stock_item=stock_item,
            vinyl_release=vinyl_release,
            quantity=int(request.POST['quantity_to_order']),
            sale_price=0,
            shop_purchase=False,
            to_become_shop_stock=True,
        )
        order_request_item.save()
        stock_item.quantity_incoming += int(request.POST['quantity_to_order'])
        stock_item.quantity_plus_quantity_incoming_stock += int(request.POST['quantity_to_order'])
        stock_item.save()
        stock_estimation = VinylRelease.objects.filter(
            catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - int(
            request.POST['quantity_to_order'])
        if stock_estimation >= 0:
            vinyl_release = stock_item.vinyl_release
            vinyl_release.stock_estimation = stock_estimation
            vinyl_release.save()
        else:
            vinyl_release.stock_estimation = 0
            vinyl_release.save()
        stock_estimation = VinylRelease.objects.filter(
            catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0]
        if stock_estimation >= 0:
            vinyl_release = stock_item.vinyl_release
            vinyl_release.stock_estimation = stock_estimation
            vinyl_release.save()
    if request.POST['master_genre_id'] != 'Master Genre Choose...':
        release.master_genre_new = Genre.objects.get(id=request.POST['master_genre_id'])
        release.save()
    #endregion
    context = {
        'library': library,
    }
    
    if 'source' in request.GET and request.GET['source'] == 'weekly_releases':
        # If the source parameter is present and equals 'weekly_releases', close the window
        return HttpResponse('Form submitted successfully and window should close.')
    else:
        # If the source parameter is not present or does not equal 'weekly_releases', render appropriate templates
        if 'previous_url' in request.POST:
            context['previous_url'] = request.POST['previous_url']
            return render(request, 'return_to_dashboard.html', context)
        else:
            return render(request, 'return_to_stock_item_add_edit_select.html', context)

def stock_item_delete_submission(request, library_id, stock_item_id):
    library = Library.objects.get(id=library_id)
    stock_item = StockItem.objects.get(id=stock_item_id)
    stock_item.delete()
    context = {
        'library': library,
    }

    return render(request, 'return_to_vinyl_shop.html', context)

def vinyl_shop(request, library_id):
    library = Library.objects.get(id=library_id)
    stock_items = StockItem.objects.filter(library=library)
    ''' update genres list
    #region update_genres
    potential_genres = []
    for i in stock_items:
        item_release = VinylRelease.objects.get(id=i.vinyl_release.pk)
        item_plates = VinylPlate.objects.filter(related_release=item_release)
        item_tracks = VinylTrack.objects.filter(related_vinyl_plate__in=item_plates)
        for j in item_tracks:
            if j.genre not in potential_genres and j.genre != '-':
                potential_genres.append(j.genre)

    shop_genres = ShopGenre.objects.filter(library=library).values_list('genre')
    for i in potential_genres:
        if i not in shop_genres:
            new_genre = ShopGenre(
                genre = Genre.objects.get(genre=i),
                library = library,
            )
            new_genre.save()
    #endregion
    '''
    ''' # update stock levels
    for i in stock_items:
        incoming_stock = OrderRequestItem.objects.filter(vinyl_release=i.vinyl_release, to_become_shop_stock=True, stockpiled=False)
        for j in incoming_stock:
            if j.quantity >= 1:
                i.quantity_incoming = j.quantity
                i.save()
            else:
                i.quantity_incoming = 0
                i.save()
        i.quantity_plus_quantity_incoming_stock = i.quantity + i.quantity_incoming
        i.save()
    '''
    ''' update stock items sleeves
    stock_items_to_update = StockItem.objects.filter(quantity__gte=1)
    for i in stock_items_to_update:
        i.has_an_outer_sleeve = True
        i.save()
    '''
    genres = ShopGenre.objects.filter(library=library)
    vibes = Vibe.objects.all()
    energy_levels = EnergyLevel.objects.all()
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    members = Member.objects.filter(
        library=library,
        active=True,
        )
    stock_items = stock_items[:0]
    recentness_options = ['New Releases', 'Recent Releases', 'Forthcoming']
    recentness_selected_option = ''
    context = {
        'library':library,
        'stock_items': stock_items,
        'shopping_cart': shopping_cart,
        'items': items,
        'genres': genres,
        'vibes': vibes,
        'energy_levels': energy_levels,
        'members': members,
        'recentness_options': recentness_options,
        'recentness_selected_option': recentness_selected_option,
    }

    return render(request,'vinyl_shop.html', context)

def vinyl_shop_search(request, library_id):
    library = Library.objects.get(id=library_id)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    stock_items = StockItem.objects.filter(library=library).order_by('vinyl_release')
    all_stock_items_length = len(stock_items)
    #region search
    search_artist = request.POST['search_artist']
    search_title = request.POST['search_title']
    search_label = request.POST['search_label']
    search_catalog = request.POST['search_catalog']
    search_genre = request.POST['search_genre']
    
    if request.POST['see_all'] == 'True':
        stock_items = stock_items
    else:
        #region search fields
        if search_artist != 'Artist...' and search_artist != None:
            stock_items = stock_items.filter(vinyl_release__related_vinyl_plate__related_vinyl_track__artist__icontains=(search_artist)).distinct()
        
        if search_title != 'Title...' and search_title != None:
            stock_items = stock_items.filter(vinyl_release__related_vinyl_plate__related_vinyl_track__title__icontains=(search_title)).distinct()
        
        if search_label != 'Label...' and search_label != None:
            stock_items = stock_items.filter(vinyl_release__label__icontains=(search_label))
        
        if search_catalog != 'Catalog...' and search_catalog != None:
            stock_items = stock_items.filter(vinyl_release__catalog_number__icontains=(search_catalog))
               
        if search_genre != 'Genre...' and search_genre != None:
            stock_items = stock_items.filter(vinyl_release__related_vinyl_plate__related_vinyl_track__genre__icontains=(search_genre)).distinct()
        #endregion
    #region new, recent and forthcoming releases
    today = date.today()
    two_weeks_ago = today - timedelta(days=21)
    two_months_ago = today - timedelta(days=48)
    recentness_selected_option = ''
    if request.POST['search_date_range'] == 'Recentness':
        stock_items = stock_items
    elif request.POST['search_date_range'] == 'New Releases':
        stock_items = stock_items.filter(vinyl_release__release_date__range=[two_weeks_ago, today])
        recentness_selected_option  = 'New Releases'
    elif request.POST['search_date_range'] == 'Recent Releases':
        stock_items = stock_items.filter(vinyl_release__release_date__range=[two_months_ago, two_weeks_ago - timedelta(days=1)])
        recentness_selected_option  = 'Recent Releases'
    elif request.POST['search_date_range'] == 'Forthcoming':
        today = date.today()
        stock_items = stock_items.filter(vinyl_release__release_date__gte=today + timedelta(days=1))
        recentness_selected_option  = 'Forthcoming'
    recentness_options = ['New Releases', 'Recent Releases', 'Forthcoming']
    if recentness_selected_option in recentness_options:
        recentness_options.remove(recentness_selected_option)
    search_results_count = stock_items.count()
    #endregion
    #endregion

    genres = ShopGenre.objects.filter(library=library)
    vibes = Vibe.objects.all()
    energy_levels = EnergyLevel.objects.all()
    members = Member.objects.filter(
        library=library, active=True)
    
    if request.POST['see_all'] == 'True':
        stock_items = stock_items
    else:
        stock_items = stock_items[:300]

    context = {
        'library':library,
        'stock_items': stock_items,
        'all_stock_items_length': all_stock_items_length,
        'search_artist': search_artist,
        'search_title': search_title,
        'search_label': search_label,
        'search_catalog': search_catalog,
        'search_genre': search_genre,
        'see_all': request.POST['see_all'],
        'recentness_selected_option': recentness_selected_option,
        'recentness_options': recentness_options,
        'search_results_count': search_results_count,
        'genres': genres,
        'vibes': vibes,
        'energy_levels': energy_levels,
        'shopping_cart': shopping_cart,
        'items': items,
        'members': members,
    }

    return render(request,'vinyl_shop.html', context)

def vinyl_shop_search_from_stock_add_edit(request, library_id): # not sure how useful this is
    library = Library.objects.get(id=library_id)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    search_catalog = request.POST['search_catalog']
    stock_items = StockItem.objects.filter(
        library=library,
        vinyl_release__catalog_number=search_catalog).order_by('vinyl_release')
    genres = ShopGenre.objects.filter(library=library)
    vibes = Vibe.objects.all()
    energy_levels = EnergyLevel.objects.all()
    members = Member.objects.filter(
        library=library,
        active=True,
        )
    context = {
        'library':library,
        'stock_items': stock_items,
        'search_catalog': search_catalog,
        'genres': genres,
        'vibes': vibes,
        'energy_levels': energy_levels,
        'shopping_cart': shopping_cart,
        'items': items,
        'members': members,
    }

    return render(request,'vinyl_shop.html', context)

def vinyl_shop_in_stock(request, library_id): # probably redundant
    library = Library.objects.get(id=library_id)

    ''' UPDATE most common genres
    stock_items = StockItem.objects.filter(library=library, status=1)
    for i in stock_items:
        if i.vinyl_release != None:
            release = i.vinyl_release
            if release.most_common == None:
                genres = []
                plates = VinylPlate.objects.filter(related_release=release)
                for p in plates:
                    tracks = VinylTrack.objects.filter(related_vinyl_plate=p)
                    for t in tracks:
                        if t.genre != '-':
                            genres.append(t.genre)
                genres = sorted(genres, key = genres.count, reverse = True)

                single_case_of_release_genres = []

                for g in genres:
                    if g not in single_case_of_release_genres:
                        single_case_of_release_genres.append(g)

                if single_case_of_release_genres[2:3]:
                    release.most_common = str(single_case_of_release_genres[:1]).strip("]'[") + ', ' + str(single_case_of_release_genres[1:2]).strip("]'[") + ', ' + str(single_case_of_release_genres[2:3]).strip("]'[")
                    release.save()
                elif single_case_of_release_genres[1:2]:
                    release.most_common = str(single_case_of_release_genres[:1]).strip("]'[") + ', ' + str(single_case_of_release_genres[1:2]).strip("]'[")
                    release.save()
                else:
                    release.most_common = str(single_case_of_release_genres[:1]).strip("]'[")
                    release.save() 
    '''
    ''' UPDATE non ordered items to status =5
    order_request_items = OrderRequestItem.objects.filter(member__user=library.library_shop, ordered=False)
    for i in order_request_items:
        if i.stock_item != None:
            if i.stock_item.quantity == 0:
                i.stock_item.status = 5
                i.stock_item.save()
    '''
    ''' UPDATE to In Stock
    for i in stock_items:
        if i.status == 2 and i.quantity >= 1:
            i.status = 2
            i.save()
    '''
    ''' UPDATE to Incoming
    for i in stock_items:
        if i.quantity <= 0 and i.quantity_incoming >= 1:
            i.status = 1
            i.save()
    '''
    ''' UPDATE less than Zero to Zero
    stock_items = StockItem.objects.filter(library=library)
    for i in stock_items:
        if i.quantity <= 0:
            i.quantity = 0
            i.save()
        if i.quantity_incoming <= 0:
            i.quantity_incoming = 0
            i.save()
        if i.quantity_plus_quantity_incoming_stock <= 0:
            i.quantity_plus_quantity_incoming_stock = 0
            i.save()
    '''

    #region count in stock items
    in_stock_items = StockItem.objects.filter(library=library).filter(quantity__gte=1)
    count = 0
    for i in in_stock_items:
        count += 1
    #endregion
    stock_items = StockItem.objects.filter(
        library=library).exclude(
            status=5)
    vinyl_in_stock = stock_items.order_by('vinyl_release__most_common', 'vinyl_release__catalog_number')

    context = {
        'library': library,
        'vinyl_in_stock': vinyl_in_stock,
        'count': count
    }

    return render(request, 'vinyl_shop_in_stock.html', context)

def vinyl_shop_in_stock_update_status_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    stock_items = StockItem.objects.filter(library=library)
    for i in stock_items:
        if i.status == 2:
            i.status = 3
            i.save()
        elif i.status == 3:
            i.status = 4
            i.save()
        elif i.status == 0:
            i.status = 5
            i.save()
    context = {
        'library': library,
    }
    
    return render(request, 'return_to_vinyl_shop_in_stock.html', context)

def vinyl_shop_in_stock_update_most_common_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    stock_items = StockItem.objects.filter(library=library)
    #region update most common
    for r in stock_items:
        if r.status != 5:
            release = VinylRelease.objects.get(catalog_number=r.vinyl_release.catalog_number)
            genres = []
            plates = VinylPlate.objects.filter(related_release__catalog_number=r)
            for p in plates:
                tracks = VinylTrack.objects.filter(related_vinyl_plate=p)
                for t in tracks:
                    if t.genre != '-':
                        genres.append(t.genre)
            if len(genres) <=0:
                if release.master_genre_new:
                    genre = Genre.objects.get(genre=release.master_genre_new.genre)
                    genres.append(str(genre.genre) + ' *Release Genre*')
            genres = sorted(genres, key = genres.count, reverse = True)

            single_case_of_release_genres = []

            for g in genres:
                if g not in single_case_of_release_genres:
                    single_case_of_release_genres.append(g)

            if single_case_of_release_genres[2:3]:
                release.most_common = str(single_case_of_release_genres[:1]).strip("]'[") + ', ' + str(single_case_of_release_genres[1:2]).strip("]'[") + ', ' + str(single_case_of_release_genres[2:3]).strip("]'[")
                release.save()
            elif single_case_of_release_genres[1:2]:
                release.most_common = str(single_case_of_release_genres[:1]).strip("]'[") + ', ' + str(single_case_of_release_genres[1:2]).strip("]'[")
                release.save()
            else:
                release.most_common = str(single_case_of_release_genres[:1]).strip("]'[")
                release.save()
    #endregion
    context = {
        'library': library,
    }
    return render(request, 'return_to_vinyl_shop_in_stock.html', context)

def return_to_vinyl_shop_in_stock(request, library_id):
    library = Library.objects.get(id=library_id)
    context = {
        'library': library,
    }
    return render(request, 'return_to_vinyl_shop_in_stock.html', context)

#endregion

