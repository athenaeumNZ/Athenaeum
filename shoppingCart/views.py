from django.shortcuts import render
from accounts.models import OrderRequestItem

from management.models import Library, Member, VinylCondition
from members.models import MemberPlate, MemberRelease, MemberReleaseStatusChoices
from musicDatabase.models import VinylPlate, VinylRelease
from shoppingCart.shopping_cart import ShoppingCart
from vinylShop.models import StockItem
from crateBuilder.views import form_variables, form_search_variables, return_location

def add_release_to_cart(request, library_id):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=request.POST['member_id'])
    stock_item = StockItem.objects.get(id=request.POST['stock_item_id'])
    shopping_cart = ShoppingCart(request)
    shopping_cart.add(stock_item=stock_item)
    context = {
        'library': library,
        'member': member,
    }
    form_variables(request, context)
    form_search_variables(request, context)
    location = return_location(context)
    return render(request, location, context)

def remove_vinyl_release_from_shopping_cart(request, library_id):
    library = Library.objects.get(id=library_id)
    stock_item = StockItem.objects.get(id=request.POST['stock_item_id'])
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    shopping_cart.remove(stock_item=stock_item)
    context = {
        'library': library,
        'shopping_cart': shopping_cart,
        'items': items,
    }
    form_variables(request, context)
    form_search_variables(request, context)
    location = return_location(context)
    return render(request, location, context)

def return_to_shopping_cart(request, library_id):
    library = Library.objects.get(id=library_id)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    context= {
        'library': library,
        'shopping_cart': shopping_cart,
        'items': items,
    }
    form_variables(request, context)
    form_search_variables(request, context)
    if 'previous_url' in request.POST and request.POST['previous_url'] == 'shopping_cart':
        context['previous_url'] = 'plate_sorter'
    return render(request, 'shopping_cart.html', context)

def shopping_cart(request, library_id):
    library = Library.objects.get(id=library_id)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    context= {
        'library': library,
        'shopping_cart': shopping_cart,
        'items': items,
    }
    form_variables(request, context)
    form_search_variables(request, context)
    return render(request, 'shopping_cart.html', context)

def shopping_cart_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    librarian = Member.objects.get(user=library.library_shop)
    shopping_cart = ShoppingCart(request)
    #region member
    member = Member.objects.get(id=request.POST['search_member'])
    to_become_shop_stock = False
    if member.is_library_shop == True:
        to_become_shop_stock = True
        library = member.library
    #endregion
    #region process shopping cart
    for item in shopping_cart:
        stock_item = StockItem.objects.get(id=item['item'].id)
        vinyl_release = VinylRelease.objects.get(catalog_number=stock_item.vinyl_release)
        #region set sale_price maybe not needed
        if to_become_shop_stock == True:
            sale_price = 0
        else:
            sale_price = stock_item.price
        #endregion
        if to_become_shop_stock == True:
        #region create shop order request item
            order_request_item = OrderRequestItem(
                library = library,
                member = librarian,
                stock_item = stock_item,
                vinyl_release = vinyl_release,
                quantity = 1,
                sale_price = 0,
                shop_purchase = False,
                to_become_shop_stock = True,
            )
            order_request_item.save()
            stock_item.quantity_incoming += 1
            stock_item.quantity_plus_quantity_incoming_stock += 1
            stock_item.save()
        #endregion
        else:
            order_request_item = None
            if stock_item.quantity >= 1:
                #region shop_purchase | in stock
                stock_item.quantity -= 1
                stock_item.quantity_plus_quantity_incoming_stock -= 1
                stock_item.save()
                if stock_item.quantity <= 0:
                    stock_item.quantity = 0
                if stock_item.quantity_incoming <= 0:
                    stock_item.quantity_incoming = 0
                if stock_item.quantity_plus_quantity_incoming_stock <= 0:
                    stock_item.quantity_plus_quantity_incoming_stock = 0

                order_request_item = OrderRequestItem(
                    library = library,
                    member = member,
                    stock_item = stock_item,
                    vinyl_release = vinyl_release,
                    quantity = 1,
                    sale_price = stock_item.price,
                    shop_purchase = True,
                    to_become_shop_stock = False,
                )
                order_request_item.save()
                #endregion
            elif stock_item.quantity <= 0 and stock_item.quantity_incoming >= 1:
                #region shop purchase | no stock on hand & Stock is incoming
                stock_item.quantity_incoming -= 1
                stock_item.quantity_plus_quantity_incoming_stock -= 1
                stock_item.save()
                set_to_ordered = False
                libraries_on_order_item = OrderRequestItem.objects.filter(
                    vinyl_release=vinyl_release,
                    member=librarian,
                    stockpiled=False,
                    quantity__gte=1)
                if libraries_on_order_item != None:
                    first_of_the_items = libraries_on_order_item.first()
                    if first_of_the_items != None:
                        if first_of_the_items.ordered == True:
                            set_to_ordered = True
                        first_of_the_items.quantity -= 1
                        first_of_the_items.quantity_used_by_member += 1
                        first_of_the_items.save()
                        if first_of_the_items.quantity == 0:
                            first_of_the_items.delete()
                order_request_item = OrderRequestItem(
                    library = library,
                    member = member,
                    stock_item = stock_item,
                    vinyl_release = vinyl_release,
                    quantity = 1,
                    sale_price = stock_item.price,
                    shop_purchase = False,
                    to_become_shop_stock = False,
                    ordered = set_to_ordered,
                )
                order_request_item.save()
                #endregion
            elif stock_item.quantity <= 0 and stock_item.quantity_incoming <= 0:
                order_request_item = OrderRequestItem(
                    library = library,
                    member = member,
                    stock_item = stock_item,
                    vinyl_release = vinyl_release,
                    quantity = 1,
                    sale_price = stock_item.price,
                    shop_purchase = False,
                    to_become_shop_stock = False,
                    ordered = False,
                )
                order_request_item.save()
            in_coming = MemberReleaseStatusChoices.objects.get(status='In Coming')
            if order_request_item != None:
                #region if member release exists | it has an order request item
                vinyl_release = order_request_item.vinyl_release
                if len(MemberRelease.objects.filter(order_request_item=order_request_item)) >= 1:
                    existing_member_release_order_request_item = MemberRelease.objects.get(
                        order_request_item=order_request_item)
                    existing_member_release_order_request_item.status = in_coming
                    existing_member_release_order_request_item.save()
                else:
                    existing_member_release_order_request_item = None
                #endregion
                if existing_member_release_order_request_item == None:
                    #region if release in want list
                    in_want_list = MemberReleaseStatusChoices.objects.get(status='In Want List')
                    if len(MemberRelease.objects.filter(member=member, vinyl_release=vinyl_release, status=in_want_list)) >= 1:
                        want_list_member_release = MemberRelease.objects.get(
                            member=order_request_item.member,
                            vinyl_release=vinyl_release,
                            status=in_want_list,
                        )
                        want_list_member_release.status = in_coming
                        want_list_member_release.save()
                    #endregion
                    else:
                        #region create member release | one does not already exist for the vinyl release
                        new_member_release = MemberRelease(
                            member = order_request_item.member,
                            vinyl_release = order_request_item.vinyl_release,
                            order_request_item = order_request_item,
                            status = in_coming,
                        )
                        new_member_release.save()
                        #endregion
                        #region create member plates
                        vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
                        vinyl_condition = VinylCondition.objects.get(condition='M')
                        for k in vinyl_plates:
                            new_member_plate = MemberPlate(
                                member=order_request_item.member,
                                member_release=new_member_release,
                                vinyl_plate=k,
                                vinyl_condition=vinyl_condition,
                            )
                            new_member_plate.save()
                        #endregion
        if stock_item.auto_restock == True and stock_item.quantity_plus_quantity_incoming_stock <= stock_item.auto_restock_threshold - 1:
            #region auto restock is on
            order_request_item = OrderRequestItem(
                library = library,
                member = librarian,
                stock_item = stock_item,
                vinyl_release = vinyl_release,
                quantity = stock_item.auto_restock_quantity,
                sale_price = 0,
                shop_purchase = False,
                to_become_shop_stock = True,
            )
            order_request_item.save()
            stock_item.quantity_incoming += stock_item.auto_restock_quantity
            stock_item.quantity_plus_quantity_incoming_stock += stock_item.auto_restock_quantity
            stock_item.save()
            stock_estimation = VinylRelease.objects.filter(catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - stock_item.auto_restock_quantity
            if stock_estimation >= 0:
                vinyl_release = stock_item.vinyl_release
                vinyl_release.stock_estimation = stock_estimation
                vinyl_release.save()
            #endregion
        else:
            #region auto restock is off
            stock_estimation = VinylRelease.objects.filter(catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - 1
            if stock_estimation >= 0:
                vinyl_release = stock_item.vinyl_release
                vinyl_release.stock_estimation = stock_estimation
                vinyl_release.save()
            #endregion
    shopping_cart.clear()
    #endregion
    context = {
        'library': library,
    }
    form_variables(request, context)
    form_search_variables(request, context)
    return render(request, 'return_to_plate_sorter.html', context)


''' OLD ????
def shopping_cart_from_plate_sorter(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    shopping_cart = ShoppingCart(request)
    items = shopping_cart.items_list
    previous_vertical_location = request.POST['previous_vertical_location']
    context= {
        'library': library,
        'member': member,
        'shopping_cart': shopping_cart,
        'items': items,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'previous_vertical_location': previous_vertical_location,
        'display_searched_releases': display_searched_releases,
    }
    return render(request, 'shopping_cart_from_plate_sorter.html', context)

def shopping_cart_from_plate_sorter_remove_item_submission(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases,):
    stock_item = StockItem.objects.get(id=request.POST['stock_item_id'])
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    shopping_cart = ShoppingCart(request)
    shopping_cart.remove(stock_item=stock_item)
    previous_vertical_location = request.POST['previous_vertical_location']
    context= {
        'library': library,
        'member': member,
        'crate_id': crate_id,
        'crate_parent_id': crate_parent_id,
        'display_stock': display_stock,
        'display_unallocated': display_unallocated,
        'previous_vertical_location': previous_vertical_location,
        'display_searched_releases': display_searched_releases,
    }
    return render(request, 'return_to_shopping_cart_from_plate_sorter.html', context)

def return_to_shopping_cart_from_plate_sorter(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
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

    return render(request, 'return_to_shopping_cart_from_plate_sorter.html', context)

def shopping_cart_submissiondqwqqw(request, library_id, member_id, crate_id, crate_parent_id, display_stock, display_unallocated, display_searched_releases):
    library = Library.objects.get(id=library_id)
    librarian = Member.objects.get(user=library.library_shop)
    shopping_cart = ShoppingCart(request)
    #region member
    if 'search_member' in request.POST:
        member = Member.objects.get(id=request.POST['search_member'])
    else:
        member = Member.objects.get(id=member_id)
    to_become_shop_stock = False
    if member.is_library_shop == True:
        to_become_shop_stock = True
        library = member.library
    #endregion
    #region process shopping cart
    for item in shopping_cart:
        stock_item = StockItem.objects.get(id=item['item'].id)
        vinyl_release = VinylRelease.objects.get(catalog_number=stock_item.vinyl_release)
        #region set sale_price maybe not needed
        if to_become_shop_stock == True:
            sale_price = 0
        else:
            sale_price = stock_item.price
        #endregion
        if to_become_shop_stock == True:
        #region create shop order request item
            order_request_item = OrderRequestItem(
                library = library,
                member = librarian,
                stock_item = stock_item,
                vinyl_release = vinyl_release,
                quantity = 1,
                sale_price = 0,
                shop_purchase = False,
                to_become_shop_stock = True,
            )
            order_request_item.save()
            stock_item.quantity_incoming += 1
            stock_item.quantity_plus_quantity_incoming_stock += 1
            stock_item.save()
        #endregion
        else:
            order_request_item = None
            if stock_item.quantity >= 1 and to_become_shop_stock == False:
                #region shop_purchase | in stock
                stock_item.quantity -= 1
                stock_item.quantity_plus_quantity_incoming_stock -= 1
                stock_item.save()
                order_request_item = OrderRequestItem(
                    library = library,
                    member = member,
                    stock_item = stock_item,
                    vinyl_release = vinyl_release,
                    quantity = 1,
                    sale_price = stock_item.price,
                    shop_purchase = True,
                    to_become_shop_stock = False,
                )
                order_request_item.save()
                #endregion
            elif stock_item.quantity <= 0 and stock_item.quantity_incoming >= 1 and to_become_shop_stock == False:
                #region shop purchase | no stock on hand & Stock is incoming
                stock_item.quantity_incoming -= 1
                stock_item.quantity_plus_quantity_incoming_stock -= 1
                stock_item.save()
                set_to_ordered = False
                libraries_on_order_item = OrderRequestItem.objects.filter(
                    vinyl_release=vinyl_release,
                    member=librarian,
                    stockpiled=False,
                    quantity__gte=1)
                if libraries_on_order_item != None:
                    first_of_the_items = libraries_on_order_item.first()
                    if first_of_the_items != None:
                        if first_of_the_items.ordered == True:
                            set_to_ordered = True
                        first_of_the_items.quantity -= 1
                        first_of_the_items.quantity_used_by_member += 1
                        first_of_the_items.save()
                        if first_of_the_items.quantity == 0:
                            first_of_the_items.delete()
                order_request_item = OrderRequestItem(
                    library = library,
                    member = member,
                    stock_item = stock_item,
                    vinyl_release = vinyl_release,
                    quantity = 1,
                    sale_price = stock_item.price,
                    shop_purchase = False,
                    to_become_shop_stock = False,
                    ordered = set_to_ordered,
                )
                order_request_item.save()
                #endregion
            in_coming = MemberReleaseStatusChoices.objects.get(status='In Coming')
            if order_request_item != None:
                #region if member release exists | it has an order request item
                vinyl_release = order_request_item.vinyl_release
                if len(MemberRelease.objects.filter(order_request_item=order_request_item)) >= 1:
                    existing_member_release_order_request_item = MemberRelease.objects.get(
                        order_request_item=order_request_item)
                    existing_member_release_order_request_item.status = in_coming
                    existing_member_release_order_request_item.save()
                else:
                    existing_member_release_order_request_item = None
                #endregion
                if existing_member_release_order_request_item == None:
                    #region if release in want list
                    in_want_list = MemberReleaseStatusChoices.objects.get(status='In Want List')
                    if len(MemberRelease.objects.filter(member=member, vinyl_release=vinyl_release, status=in_want_list)) >= 1:
                        want_list_member_release = MemberRelease.objects.get(
                            member=order_request_item.member,
                            vinyl_release=vinyl_release,
                            status=in_want_list,
                        )
                        want_list_member_release.status = in_coming
                        want_list_member_release.save()
                    #endregion
                    else:
                        #region create member release | one does not already exist for the vinyl release
                        new_member_release = MemberRelease(
                            member = order_request_item.member,
                            vinyl_release = order_request_item.vinyl_release,
                            order_request_item = order_request_item,
                            status = in_coming,
                        )
                        new_member_release.save()
                        #endregion
                        #region create member plates
                        vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)
                        vinyl_condition = VinylCondition.objects.get(condition='M')
                        for k in vinyl_plates:
                            new_member_plate = MemberPlate(
                                member=order_request_item.member,
                                member_release=new_member_release,
                                vinyl_plate=k,
                                vinyl_condition=vinyl_condition,
                            )
                            new_member_plate.save()
                        #endregion
        if stock_item.auto_restock == True and stock_item.quantity_plus_quantity_incoming_stock <= stock_item.auto_restock_threshold - 1:
            #region auto restock is on
            order_request_item = OrderRequestItem(
                library = library,
                member = librarian,
                stock_item = stock_item,
                vinyl_release = vinyl_release,
                quantity = stock_item.auto_restock_quantity,
                sale_price = 0,
                shop_purchase = False,
                to_become_shop_stock = True,
            )
            order_request_item.save()
            stock_item.quantity_incoming += stock_item.auto_restock_quantity
            stock_item.quantity_plus_quantity_incoming_stock += stock_item.auto_restock_quantity
            stock_item.save()
            stock_estimation = VinylRelease.objects.filter(catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - stock_item.auto_restock_quantity
            if stock_estimation >= 0:
                vinyl_release = stock_item.vinyl_release
                vinyl_release.stock_estimation = stock_estimation
                vinyl_release.save()
            #endregion
        else:
            #region auto restock is off
            stock_estimation = VinylRelease.objects.filter(catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - 1
            if stock_estimation >= 0:
                vinyl_release = stock_item.vinyl_release
                vinyl_release.stock_estimation = stock_estimation
                vinyl_release.save()
            #endregion
    shopping_cart.clear()
    #endregion
    #region previous vertical location
    if 'previous_vertical_location' in request.POST:
        previous_vertical_location = request.POST['previous_vertical_location']
    else:
        previous_vertical_location = 0
    #endregion
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

def shopping_cart_add_item(request, library_id, stock_item_id):
    library = Library.objects.get(id=library_id)
    stock_item = StockItem.objects.get(id=stock_item_id)
    shopping_cart = ShoppingCart(request)
    shopping_cart.add(stock_item=stock_item)
    context = {
        'library': library,
    }
    return render(request, 'return_to_vinyl_shop.html', context)
    
def shopping_cart_remove_item(request, library_id, stock_item_id):
    library = Library.objects.get(id=library_id)
    shopping_cart = ShoppingCart(request)
    stock_item = StockItem.objects.get(id=stock_item_id)
    shopping_cart.remove(stock_item=stock_item)
    context = {
        'library': library,
        'shopping_cart': shopping_cart
    }
    return render(request, 'return_to_vinyl_shop.html', context)

def shopping_cart_submissionz(request, library_id):
    library = Library.objects.get(id=library_id)
    librarian = Member.objects.get(user=library.library_shop)
    shopping_cart = ShoppingCart(request)
    
    #region member
    member = Member.objects.get(id=request.POST['search_member'])
    to_become_shop_stock = False
    if member.is_library_shop == True:
        to_become_shop_stock = True
        library = member.library
    #endregion
    for item in shopping_cart:
        stock_item = StockItem.objects.get(id=item['item'].id)
        vinyl_release = VinylRelease.objects.get(catalog_number=stock_item.vinyl_release)
        #region set sale_price maybe not needed
        if to_become_shop_stock == True:
            sale_price = 0
        else:
            sale_price = stock_item.price
        #endregion
        if to_become_shop_stock == True:
            order_request_item = OrderRequestItem(
                library = library,
                member = librarian,
                stock_item = stock_item,
                vinyl_release = vinyl_release,
                quantity = 1,
                sale_price = 0,
                shop_purchase = False,
                to_become_shop_stock = True,
            )
            order_request_item.save()
            stock_item.quantity_incoming += 1
            stock_item.quantity_plus_quantity_incoming_stock += 1
            stock_item.save()
        else:
            if stock_item.quantity >= 1 and to_become_shop_stock == False:
                stock_item.quantity -= 1
                stock_item.quantity_plus_quantity_incoming_stock -= 1
                stock_item.save()
                order_request_item = OrderRequestItem(
                    library = library,
                    member = member,
                    stock_item = stock_item,
                    vinyl_release = vinyl_release,
                    quantity = 1,
                    sale_price = stock_item.price,
                    shop_purchase = True,
                    to_become_shop_stock = False,
                )
                order_request_item.save()
                # auto restock

            elif stock_item.quantity <= 0 and stock_item.quantity_incoming >= 1 and to_become_shop_stock == False:
                stock_item.quantity_incoming -= 1
                stock_item.quantity_plus_quantity_incoming_stock -= 1
                stock_item.save()
                set_to_ordered = False
                libraries_on_order_item = OrderRequestItem.objects.filter(
                    vinyl_release=vinyl_release,
                    member=librarian,
                    stockpiled=False,
                    quantity__gte=1)
                if libraries_on_order_item != None:
                    first_of_the_items = libraries_on_order_item.first()
                    if first_of_the_items != None:
                        if first_of_the_items.ordered == True:
                            set_to_ordered = True
                        first_of_the_items.quantity -= 1
                        first_of_the_items.quantity_used_by_member += 1
                        first_of_the_items.save()
                        if first_of_the_items.quantity == 0:
                            first_of_the_items.delete()
                order_request_item = OrderRequestItem(
                    library = library,
                    member = member,
                    stock_item = stock_item,
                    vinyl_release = vinyl_release,
                    quantity = 1,
                    sale_price = stock_item.price,
                    shop_purchase = False,
                    to_become_shop_stock = False,
                    ordered = set_to_ordered,
                )
                order_request_item.save()
            else: #I think this is redundant?
                order_request_item = OrderRequestItem(
                    library = library,
                    member = member,
                    stock_item = stock_item,
                    vinyl_release = vinyl_release,
                    quantity = 1,
                    sale_price = sale_price,
                    shop_purchase = False,
                    to_become_shop_stock = False,
                )
                order_request_item.save()

        if stock_item.auto_restock == True and stock_item.quantity_plus_quantity_incoming_stock <= stock_item.auto_restock_threshold - 1:
            order_request_item = OrderRequestItem(
                library = library,
                member = librarian,
                stock_item = stock_item,
                vinyl_release = vinyl_release,
                quantity = stock_item.auto_restock_quantity,
                sale_price = 0,
                shop_purchase = False,
                to_become_shop_stock = True,
            )
            order_request_item.save()
            stock_item.quantity_incoming += stock_item.auto_restock_quantity
            stock_item.quantity_plus_quantity_incoming_stock += stock_item.auto_restock_quantity
            stock_item.save()
            stock_estimation = VinylRelease.objects.filter(catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - stock_item.auto_restock_quantity
            if stock_estimation >= 0:
                vinyl_release.stock_estimation = stock_estimation
                vinyl_release.save()
        else:
            stock_estimation = VinylRelease.objects.filter(catalog_number=stock_item.vinyl_release).values_list('stock_estimation', flat=True)[0] - 1
            if stock_estimation >= 0:
                vinyl_release.stock_estimation = stock_estimation
                vinyl_release.save()

    shopping_cart.clear()
    
    context = {
        'library': library,
        'member': member,
    }

    return render(request, 'return_to_member_dashboard.html', context)
'''
''' OLD shopping_cart_submission
def shopping_cart_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    shopping_cart = ShoppingCart(request)

    order_request = OrderRequest(
        library=library,
        member_id=request.POST['search_member'],
        )
    order_request.save()

    for item in shopping_cart:
        stock_item = item['item']
        vinyl_release = VinylRelease.objects.get(id=stock_item.vinyl_release.id)
        #region check availability
        check_availability = False
        if vinyl_release.stock_estimation == 0 and stock_item.quantity <= 0:
            check_availability = True
        #endregion
        order_request_item = OrderRequestItem(
            order_request = order_request,
            vinyl_release = vinyl_release,
            shop_purchase = True,
            sale_price = stock_item.price,
            check_availability = check_availability, # check availability
            )
        order_request_item.save()
        
        if order_request_item.check_availability == True:
            dog = "dog"
            
        stock_item.quantity -= 1
        stock_item.save()

    shopping_cart.clear()
    
    context = {
        'library': library,
        'order_request': order_request,
    }

    return render(request, 'return_to_order_request.html', context)
'''
''' OLD
# old shopping cast submission
def shopping_cart_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    shopping_cart = ShoppingCart(request)

    order_request = OrderRequest(
        library=library,
        member_id=request.POST['search_member'],
        )
    order_request.save()

    invoice = Invoice(
        library=library,
        member = order_request.member,
        direct_shopping_invoice = True,
        flattened_shipping_price = 0,
        )
    invoice.save()

    for item in shopping_cart:
        
        stock_item = item['item']

        vinyl_release = VinylRelease.objects.get(id=stock_item.vinyl_release.id)
        order_request_item = OrderRequestItem(
            order_request=order_request,
            vinyl_release=vinyl_release,
            ordered=True,
            sent_to_invoice_receipt=True,
            invoiced=True,
            to_direct_shopping_invoice = True,
            )
        order_request_item.save()

        invoice_item = InvoiceItem(
            order_request_item=order_request_item,
            invoice=invoice,
            flattened_price = item['price'],
            )
        invoice_item.save()

        stock_item.quantity -= 1
        stock_item.save()

    shopping_cart.clear()
    
    context = {
        'library': library,
        'invoice': invoice,
 
    }

    return render(request, 'return_to_invoice.html', context)

# return to cart
def return_to_cart(request, library_id):
    library = Library.objects.get(id=library_id)
    context = {
        'library': library
    }
    return render(request,'return_to_cart.html', context)

#endregion

#region invoice ################
# invoice
def member_order(request, library_id, order_id, member_id):
    library = Library.objects.get(id=library_id)
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)
    member = order.member
    
    for item in order_items:
        if item.library_plate == None:
            item.location = 'Placing Order'
        elif member.membership_number in item.library_plate.related_sub_crate.sub_crate_id :
            library_plates = LibraryPlate.objects.filter(contributor=order.member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number)
            for plate in library_plates:
                for item in order_items:
                    if plate == item.library_plate:
                        item.location = plate.related_sub_crate
                        item.location = str(item.location)[7:][:-4]
        else:
            library_plates = LibraryPlate.objects.filter(contributor=order.member)
            for plate in library_plates:
                for item in order_items:
                    if plate == item.library_plate:
                        item.location = plate.related_sub_crate
                        if plate.related_sub_crate.master_library_crate.crate_type == 'Mix':
                            item.location = str(item.location)[:-4]
                        else:
                            item.location = str(item.location)

    member = Member.objects.get(id=member_id)
    member_want_list = MemberWantlist.objects.get(member=member)

    library_in_coming_stock = LibraryPlate.objects.filter(
        contributor=member).filter(
        related_sub_crate__sub_crate_id__icontains="On Order").values_list(
        'related_vinyl_plate__related_release__id', flat=True)
    
    library_in_stock = LibraryPlate.objects.filter(
        contributor=member).filter(
        related_sub_crate__sub_crate_id__icontains="Sale Vinyl").values_list(
        'related_vinyl_plate__related_release__id', flat=True)
    
    context = {
        'library': library,
        'member_want_list':member_want_list,
        'library_in_coming_stock': library_in_coming_stock,
        'library_in_stock': library_in_stock,
        'order': order,
        'order_items': order_items,
        'member': member,

    }

    return render(request,'member_order.html', context)

def invoice_cashbook_entry_add_submission(request, library_id, order_id):
    library = Library.objects.get(id=library_id)
    order = Order.objects.get(id=order_id)
    invoice_type = InvoiceType.objects.get(type__icontains='Sales')
    member = Member.objects.get(id=order.member.pk)
    amount_NZD = order.get_total_cost()
    is_expense = False
    invoice_reference =  str('INV-' + format(order.pk, '06d'))
    bank_account_used = 1
    reconciled = False
    invoice_type = invoice_type.pk
    gst_included = True
    gst_should_be_included = True
    processing_date = order.created
    invoice_date = order.created

    entry = CashBookEntry(
        amount_NZD=amount_NZD,
        is_expense=is_expense,
        invoice_reference=invoice_reference, 
        bank_account_used_id=bank_account_used,
        reconciled=reconciled, 
        invoice_type_id=invoice_type,
        gst_included=gst_included,
        gst_should_be_included=gst_should_be_included,
        library=library,
        processing_date=processing_date,
        invoice_date=invoice_date,
        )
    entry.save()

    order.cashbook_entry_added = True
    order.save()

    context = {
        'library': library,
        'order': order,
        'member': member
    }
    return render(request, 'return_to_member_order.html', context)

def invoice_item_update(request, library_id, order_id, order_item_id):
    library = Library.objects.get(id=library_id)
    order_item = OrderItem.objects.get(id=order_item_id)
    order = Order.objects.get(id=order_id)

    context = {
        'library': library,
        'order': order,
        'order_item': order_item,
    }

    return render(request, 'invoice_item_update.html', context)

def invoice_item_update_submission(request, library_id, order_id, order_item_id):
    library = Library.objects.get(id=library_id)
    order_item = OrderItem.objects.get(id=order_item_id)

    if request.method == 'POST':
        order_item.quantity = request.POST['quantity']
        order_item.price = request.POST['price']
        order_item.save()

    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)

    context = {
        'library': library,
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'return_to_invoice.html', context)

def invoice_pay_submission(request, library_id, order_id):
    library = Library.objects.get(id=library_id)
    order = Order.objects.get(id=order_id)  

    order.paid = True
    order.save()   

    context = {
        'library': library,
        'order': order,
    }

    return render(request, 'return_to_member_order.html', context)

# invoice order items submission
def invoice_order_items_submission(request, library_id, order_id):
    library = Library.objects.get(id=library_id)
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)  

    order.on_order = True
    order.save()  

    context = {
        'library': library,
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'return_to_member_order.html', context)

# invoice order order ITEM submission
def invoice_order_item_submission(request, library_id, order_id, order_item_id):
    library = Library.objects.get(id=library_id)
    order_item = OrderItem.objects.get(id=order_item_id)

    for item in range(0, order_item.quantity):
        release_id = order_item.vinyl_release.id
        vinyl_release = VinylRelease.objects.get(id=release_id)
        if VinylRelease.objects.filter(id=release_id).values_list('stock_estimation',flat=True)[0] != 1:
            vinyl_release.stock_estimation = VinylRelease.objects.filter(id=release_id).values_list('stock_estimation',flat=True)[0] - 1
            vinyl_release.save()
        vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)

        library_crate_id = 'Member ' + order_item.order.library.name[:3].upper()
        pending_crate_id = LibraryCrate.objects.get(library_crate_id=library_crate_id).id

        library_sub_crate_id = str(order_item.order.member.membership_number) + ' On Order ' + str(order_item.order.library.name)[:3].upper()
        processing_order_crate_id = SubCrate.objects.get(sub_crate_id=library_sub_crate_id).id

        for i in range(0, len(vinyl_plates) ):
            plate = LibraryPlate(
                related_vinyl_plate_id=vinyl_plates[i].id,
                related_library_crate_id = pending_crate_id, 
                contributor_id=order_item.order.member.id,
                media_condition= 'M',
                related_sub_crate_id = processing_order_crate_id
                )
            plate.save() 
            # vinyl_colour
            if vinyl_release.vinyl_colour:
                plate.vinyl_colour = vinyl_release.vinyl_colour
                plate.save()
            else:
                plate.vinyl_colour = 'Choose...'
                plate.save()
            # plate size
            if vinyl_release.plate_size:
                plate.plate_size = vinyl_release.plate_size
                plate.save()
            else:
                plate.plate_size = 'Choose...'
                plate.save()
            # cover
            if vinyl_release.sleeve_type:
                plate.cover = vinyl_release.sleeve_type
                plate.save()
            else:
                plate.cover = 'Choose...'
                plate.save()
            # release type
            if vinyl_release.release_type:
                plate.release_type = vinyl_release.release_type
                plate.save()
            else:
                plate.release_type = 'Choose...'
                plate.save()        

    order_item.ordered = True
    order_item.save()

    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)

    context = {
        'library': library,
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'return_to_member_order.html', context)

# invoice order order ITEM submission
def invoice_order_get_item_found_in_stock_submission(request, library_id, order_id, order_item_id):
    library = Library.objects.get(id=library_id)
    order_item = OrderItem.objects.get(id=order_item_id)

    members_stockpile_sub_crate_id = str(order_item.order.member.membership_number) + ' Stockpile ' + str(order_item.order.library.name)[:3].upper()
    members_stockpile_crate = SubCrate.objects.get(sub_crate_id=members_stockpile_sub_crate_id)

    library_plates_to_swap_for = []
    for item in range(0, order_item.quantity):

        vinyl_plates = VinylPlate.objects.filter(related_release=order_item.vinyl_release)
         
        for i in vinyl_plates:
            plate = LibraryPlate.objects.filter(
                related_sub_crate__sub_crate_id__icontains='Sale Vinyl').filter(
                related_sub_crate__master_library_crate__library=library).filter(
                related_vinyl_plate=i).first()
            order_item.library_plate = plate
            order_item.save()
            plate.related_sub_crate = members_stockpile_crate
            plate.save()
            library_plates_to_swap_for.append(plate)



    for i in library_plates_to_swap_for:
        plater = i
        plater.contributor = order_item.order.member
        plater.related_sub_crate = members_stockpile_crate
        plater.save()    

    order_item.ordered = True
    order_item.save()

    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)

    context = {
        'library': library,
        'order': order,
        'order_items': order_items,
        'library_plates_to_swap_for': library_plates_to_swap_for
    }

    return render(request, 'return_to_member_order.html', context)

# invoice order order ITEM submission
def invoice_order_get_item_found_in_on_order_submission(request, library_id, order_id, order_item_id):
    library = Library.objects.get(id=library_id)
    order_item = OrderItem.objects.get(id=order_item_id)

    swapping_member = Member.objects.get(id=order_item.order.member.pk)
    
    members_on_order_sub_crate_id = str(swapping_member.membership_number) + ' On Order ' + str(swapping_member.library)[:3].upper()

    members_on_order_crate = SubCrate.objects.get(sub_crate_id=members_on_order_sub_crate_id)

    library_crate_id = 'Member ' + str(swapping_member.library)[:3].upper()
    library_crate = LibraryCrate.objects.get(library_crate_id=library_crate_id)

    library_plates_to_swap_for = []

    vinyl_plates = VinylPlate.objects.filter(related_release=order_item.vinyl_release)
        
    for i in vinyl_plates:
        plate = LibraryPlate.objects.filter(
            related_sub_crate__sub_crate_id__icontains='On Order').filter(
            related_sub_crate__master_library_crate__library=library).filter(
            related_vinyl_plate=i).first()
        library_plates_to_swap_for.append(plate)


    for i in library_plates_to_swap_for:
        i.contributor = Member.objects.get(id=swapping_member.pk)
        i.related_sub_crate = members_on_order_crate
        i.related_library_crate = library_crate
        i.save()    

    order_item.ordered = True
    order_item.save()

    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)

    context = {
        'library': library,
        'order': order,
        'order_items': order_items,
        'library_plates_to_swap_for': library_plates_to_swap_for
    }

    return render(request, 'return_to_member_order.html', context)


# invoice order items submission
def invoice_sell_in_stock_items_to_member_submission(request, library_id, order_id):
    library = Library.objects.get(id=library_id)
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)

    for i in order_items:
        release_id = item.vinyl_release.id


    for i in range(0, len(order_items)):
        item = order_items[i]
        release_id = item.vinyl_release.id
        vinyl_release = VinylRelease.objects.get(id=release_id)
        vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)

        library_crate_id = 'Member ' + order.library.name[:3].upper()
        pending_crate_id = LibraryCrate.objects.get(library_crate_id=library_crate_id).id

        library_sub_crate_id = str(order.member.membership_number) + ' Stockpile ' + str(order.library.name)[:3].upper()
        processing_order_crate_id = SubCrate.objects.get(sub_crate_id=library_sub_crate_id).id

        for i in range(0, len(vinyl_plates) ):
            plate = LibraryPlate(
                related_vinyl_plate_id=vinyl_plates[i].id,
                related_library_crate_id = pending_crate_id, 
                contributor_id=order.member.id,
                media_condition= 'M',
                related_sub_crate_id = processing_order_crate_id
                )
            plate.save() 
            # vinyl_colour
            if vinyl_release.vinyl_colour:
                plate.vinyl_colour = vinyl_release.vinyl_colour
                plate.save()
            else:
                plate.vinyl_colour = 'Choose...'
                plate.save()
            # plate size
            if vinyl_release.plate_size:
                plate.plate_size = vinyl_release.plate_size
                plate.save()
            else:
                plate.plate_size = 'Choose...'
                plate.save()
            # cover
            if vinyl_release.sleeve_type:
                plate.cover = vinyl_release.sleeve_type
                plate.save()
            else:
                plate.cover = 'Choose...'
                plate.save()
            # release type
            if vinyl_release.release_type:
                plate.release_type = vinyl_release.release_type
                plate.save()
            else:
                plate.release_type = 'Choose...'
                plate.save()

            item.library_plate = plate
            item.save()         

    order.on_order = True
    order.save()  

    context = {
        'library': library,
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'return_to_invoice.html', context)

# invoice pay submission
def invoice_remove_mark_up_submission(request, library_id, order_id):
    library = Library.objects.get(id=library_id)
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order_id=order_id)

    for i in order_items:
        i.price = i.vinyl_release.floating_no_mark_up_price_NZ
        i.save()
    order.mark_up_removed = True
    order.save()
    
    context = {
        'library': library,
        'order': order,
        'order_items': order_items,
    }

    return render(request, 'return_to_invoice.html', context)

# invoice use credit submission
def invoice_use_credit_submission(request, library_id, order_id):
    library = Library.objects.get(id=library_id)
    order = Order.objects.get(id=order_id)
    member = Member.objects.get(membership_number=order.member.membership_number)
    # minus the credit form the total cost
    total_cost = Decimal(order.get_total_cost())

    members_accout_credit = member.account_credit
    cost_after_credit = total_cost - members_accout_credit
    if cost_after_credit <= 0:
        order.credit_used = total_cost
        member.account_credit = members_accout_credit - total_cost
    else:
        order.credit_used = members_accout_credit
        member.account_credit = 0
    order.save()
    member.save()
    
    context = {
        'library': library,
        'order': order,
    }

    return render(request, 'return_to_invoice.html', context)

# return to invoice
def return_to_member_order(request, library_id, order_id):
    library = Library.objects.get(id=library_id)
    order = Order.objects.get(id=order_id)
    member = order.member
    
    context = {
        'library': library,
        'order': order,
        'member': member,
    }

    return render(request, 'return_to_member_order.html', context)

#endregion

#region purchase order ################

def cart_purchase_order_submission(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    cart = Cart(request)
    if request.method == 'POST':
        member = request.POST['search_member']
        purchase_order = PurchaseOrder(library=library, member_id=member)
        purchase_order.save()
    else:
        member = Member.objects.get(id=member_id)
        purchase_order = PurchaseOrder(library=library, member=member)
        purchase_order.save()

    for item in cart:
        PurchaseOrderItem.objects.create(purchase_order=purchase_order, vinyl_release=item['vinyl_release'], price=item['no_markup_price'])

    cart.clear()

    request.session['order_id'] = purchase_order.pk
    
    context = {
        'library': library,
        'cart': cart,
        'purchase_order': purchase_order,
    }
    return render(request, 'return_to_purchase_order_receipt.html', context)

def purchase_order_order_items_submission(request, library_id, purchase_order_id):
    library = Library.objects.get(id=library_id)
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    order_items = PurchaseOrderItem.objects.filter(purchase_order_id=purchase_order_id)

    purchase_order.on_order = True
    purchase_order.save()  

    context = {
        'library': library,
        'purchase_order': purchase_order,
        'order_items': order_items,
    }

    return render(request, 'return_to_purchase_order_receipt.html', context)

def purchase_order_funded_submission(request, library_id, purchase_order_id):
    library = Library.objects.get(id=library_id)
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    order_items = PurchaseOrderItem.objects.filter(purchase_order_id=purchase_order_id)

    purchase_order.funded = True
    purchase_order.save()  

    context = {
        'library': library,
        'purchase_order': purchase_order,
        'order_items': order_items,
    }

    return render(request, 'return_to_purchase_order_receipt.html', context)

def purchase_order_is_restock_submission(request, library_id, purchase_order_id):
    library = Library.objects.get(id=library_id)
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    order_items = PurchaseOrderItem.objects.filter(purchase_order_id=purchase_order_id)

    purchase_order.is_restock = True
    purchase_order.save()  

    context = {
        'library': library,
        'purchase_order': purchase_order,
        'order_items': order_items,
    }

    return render(request, 'return_to_purchase_order_receipt.html', context)

def purchase_order_cashbook_entry_add_submission(request, library_id, purchase_order_id):
    library = Library.objects.get(id=library_id)
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    invoice_type = InvoiceType.objects.get(type__icontains='Funds Introduced')
    order_items = PurchaseOrderItem.objects.filter(purchase_order_id=purchase_order_id)

    amount_NZD = purchase_order.order_total()
    is_expense = False
    invoice_reference =  str('ORDER-' + format(purchase_order.pk, '03d'))
    bank_account_used = 1
    reconciled = False
    invoice_type = invoice_type.pk
    gst_included = False
    gst_should_be_included = False
    processing_date = purchase_order.created

    entry = CashBookEntry(
        amount_NZD=amount_NZD,
        is_expense=is_expense,
        invoice_reference=invoice_reference, 
        bank_account_used_id=bank_account_used,
        reconciled=reconciled, 
        invoice_type_id=invoice_type,
        gst_included=gst_included,
        gst_should_be_included=gst_should_be_included,
        library=library,
        processing_date=processing_date,
        )
    entry.save()

    purchase_order.cashbook_entry_added = True
    purchase_order.save()

    context = {
        'library': library,
        'order_items': order_items,
        'purchase_order': purchase_order,
    }
    return render(request, 'return_to_purchase_order_receipt.html', context)

def purchase_order_order_item_submission(request, library_id, purchase_order_id, purchase_order_item_id):
    library = Library.objects.get(id=library_id)
    order_item = PurchaseOrderItem.objects.get(id=purchase_order_item_id)

    for item in range(0, order_item.quantity):
        release_id = order_item.vinyl_release.id
        vinyl_release = VinylRelease.objects.get(id=release_id)
        vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release)

        library_crate_id = 'Member ' + order_item.purchase_order.library.name[:3].upper()
        pending_crate_id = LibraryCrate.objects.get(library_crate_id=library_crate_id).id

        library_sub_crate_id = str(order_item.purchase_order.member.membership_number) + ' On Order ' + str(order_item.purchase_order.library.name)[:3].upper()
        processing_order_crate_id = SubCrate.objects.get(sub_crate_id=library_sub_crate_id).id

        for i in range(0, len(vinyl_plates) ):
            plate = LibraryPlate(
                related_vinyl_plate_id=vinyl_plates[i].id,
                related_library_crate_id = pending_crate_id, 
                contributor_id=order_item.purchase_order.member.id,
                media_condition= 'M',
                related_sub_crate_id = processing_order_crate_id
                )
            plate.save() 
            # vinyl_colour
            if vinyl_release.vinyl_colour:
                plate.vinyl_colour = vinyl_release.vinyl_colour
                plate.save()
            else:
                plate.vinyl_colour = 'Choose...'
                plate.save()
            # plate size
            if vinyl_release.plate_size:
                plate.plate_size = vinyl_release.plate_size
                plate.save()
            else:
                plate.plate_size = 'Choose...'
                plate.save()
            # cover
            if vinyl_release.sleeve_type:
                plate.cover = vinyl_release.sleeve_type
                plate.save()
            else:
                plate.cover = 'Choose...'
                plate.save()
            # release type
            if vinyl_release.release_type:
                plate.release_type = vinyl_release.release_type
                plate.save()
            else:
                plate.release_type = 'Choose...'
                plate.save()        

    order_item.ordered = True
    order_item.save()

    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    order_items = PurchaseOrderItem.objects.filter(purchase_order_id=purchase_order_id)

    context = {
        'library': library,
        'purchase_order': purchase_order,
        'order_items': order_items,
    }

    return render(request, 'return_to_purchase_order_receipt.html', context)

def purchase_order_order_item_update(request, library_id, purchase_order_id, purchase_order_item_id):
    library = Library.objects.get(id=library_id)
    purchase_order_item = PurchaseOrderItem.objects.get(id=purchase_order_item_id)
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)

    context = {
        'library': library,
        'purchase_order': purchase_order,
        'purchase_order_item': purchase_order_item,
    }

    return render(request, 'purchase_order_order_item_update.html', context)

def purchase_order_order_item_update_submission(request, library_id, purchase_order_id, purchase_order_item_id):
    library = Library.objects.get(id=library_id)
    order_item = PurchaseOrderItem.objects.get(id=purchase_order_item_id)

    if request.method == 'POST':
        order_item.quantity = request.POST['quantity']
        order_item.price = request.POST['price']
        order_item.save()

    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    order_items = PurchaseOrderItem.objects.filter(purchase_order_id=purchase_order_id)

    context = {
        'library': library,
        'purchase_order': purchase_order,
        'order_items': order_items,
    }

    return render(request, 'return_to_purchase_order_receipt.html', context)

def purchase_order_receipt(request, library_id, purchase_order_id):
    library = Library.objects.get(id=library_id)
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    purchase_order_items = PurchaseOrderItem.objects.filter(purchase_order_id=purchase_order_id).order_by('vinyl_release__supplier__name', 'vinyl_release__catalog_number')
    member = purchase_order.member
    
    for item in purchase_order_items:
        if item.library_plate == None:
            item.location = 'Placing Order'
        elif member.membership_number in item.library_plate.related_sub_crate.sub_crate_id :
            library_plates = LibraryPlate.objects.filter(contributor=purchase_order.member).filter(related_sub_crate__sub_crate_id__contains=member.membership_number)
            for plate in library_plates:
                for item in purchase_order_items:
                    if plate == item.library_plate:
                        item.location = plate.related_sub_crate
                        item.location = str(item.location)[7:][:-4]
        else:
            library_plates = LibraryPlate.objects.filter(contributor=purchase_order.member)
            for plate in library_plates:
                for item in purchase_order_items:
                    if plate == item.library_plate:
                        item.location = plate.related_sub_crate
                        if plate.related_sub_crate.master_library_crate.crate_type == 'Mix':
                            item.location = str(item.location)[:-4]
                        else:
                            item.location = str(item.location)

    context = {
        'library': library,
        'purchase_order': purchase_order,
        'purchase_order_items': purchase_order_items,
        'member': member,

    }

    return render(request,'purchase_order_receipt.html', context)

def return_to_purchase_order_receipt(request, library_id, purchase_order_id):
    library = Library.objects.get(id=library_id)
    purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
    member = purchase_order.member
    
    context = {
        'library': library,
        'purchase_order': purchase_order,
        'member': member,
    }

    return render(request, 'return_to_purchase_order_receipt.html', context)

#endregion

'''
