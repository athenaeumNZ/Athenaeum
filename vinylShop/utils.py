from musicDatabase.models import VinylRelease, VinylDistributor


def convert_stock_items_to_vinyl_releases_util(stock_items):
    vinyl_releases = []
    for i in stock_items:
        vinyl_releases.append(i.vinyl_release)
    return vinyl_releases

def update_not_black_util(vinyl_releases):
    for i in vinyl_releases:
        if i.vinyl_colour == 'Black':
            i.not_black = False
            i.save()
        elif i.vinyl_colour != None:
            i.not_black = True
            i.save()
    return vinyl_releases

def update_stock_items_vinyl_releases_not_black_util(stock_items):
    vinyl_releases = convert_stock_items_to_vinyl_releases_util(stock_items)
    vinyl_releases = update_not_black_util(vinyl_releases)
    return vinyl_releases

def change_label_distributor(label_name, distributor_code_current, distributor_code_to_update_to):
    vinyl_releases = VinylRelease.objects.filter(
        label__icontains=label_name,
        distributor__distributor_code__icontains=distributor_code_current)
    distributor_to_update_to = VinylDistributor.objects.get(distributor_code__icontains=distributor_code_to_update_to)
    for i in vinyl_releases:
        i.distributor = distributor_to_update_to
        i.save()
    return vinyl_releases

'''

# Get the quantity to order from the POST data
quantity_to_order = int(request.POST['quantity_to_order'])

# Iterate over the rows of the table
for i in range(quantity_to_order):
    # Create an order request item for each copy
    order_request_item = OrderRequestItem(
        library=library,
        member=librarian,
        stock_item=ordering_stock_item,
        vinyl_release=release,
        quantity=1,  # Since we're creating one copy at a time
        sale_price=0,
        shop_purchase=False,
        to_become_shop_stock=True,
    )
    order_request_item.save()

    # Increment the incoming quantity for the stock item
    ordering_stock_item.quantity_incoming += 1
    ordering_stock_item.quantity_plus_quantity_incoming_stock += 1
    ordering_stock_item.save()

    # Update the stock estimation for the release
    stock_estimation = max(VinylRelease.objects.filter(catalog_number=ordering_stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - 1, 0)
    ordering_stock_item.vinyl_release.stock_estimation = stock_estimation
    ordering_stock_item.vinyl_release.save()
'''

def stock_item_add_edit_order_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    if request.method == "POST":
        # Get the release ID and quantity from the request
        release_id = request.POST.get('releaseId')
        quantity_to_order = int(request.POST.get('quantity'))
        current_stock_items = StockItem.objects.filter(library=library)
        current_stock_items_releases = current_stock_items.values_list("vinyl_release__catalog_number", flat=True)
        release = VinylRelease.objects.get(id=release_id)
        if release.catalog_number in current_stock_items_releases:
            stock_item = StockItem.objects.get(vinyl_release=release)
            stock_item.quantity += quantity_to_order
            stock_item.save()
            ordering_stock_item = stock_item
        else:
            new_stock_item = StockItem(
                library = library,
                vinyl_release = release,
                quantity = request.POST['quantity'],
                price = 999,
                auto_restock_threshold = 1,
                auto_restock_quantity = 1,
                updated_by_library_shop = True
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

        # Return a response if needed
        return HttpResponse("Order placed successfully")  # Or any appropriate response
    else:
        # Handle GET requests or invalid requests
        return HttpResponseBadRequest()
    
def update_stock_levels_all(library_id):
    library = Library.objects.get(id=library_id)
    stock_items = StockItem.objects.filter(library=library)
    member = Member.objects.get(user=library.library_shop)
    order_request_items = OrderRequestItem.objects.filter(member=member, stockpiled=False)
    for i in stock_items:
        i.quantity_incoming = 0
        i.save()
        i.quantity_plus_quantity_incoming_stock = i.quantity
        i.save()
        for j in order_request_items:
            if i.vinyl_release == j.vinyl_release:
                i.quantity_incoming += j.quantity
                i.quantity_plus_quantity_incoming_stock += j.quantity
                i.save()
    return order_request_items