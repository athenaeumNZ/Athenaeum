from decimal import Decimal
from django.shortcuts import render
from django.urls import resolve

from cart.cart import Cart
from cart.models import Order, OrderItem, PurchaseOrder, PurchaseOrderItem
from management.models import Library, Member
from musicDatabase.models import VinylPlate, VinylRelease
from vinylLibrary.models import LibraryPlate, LibraryCrate, SubCrate

#region cart ################
# cart
def cart(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    cart = Cart(request)
    members = Member.objects.filter(library=library)

    move_and_swap_crates = SubCrate.objects.filter(
        master_library_crate__library=library).filter(
        sub_crate_id__icontains='Stockpile')
    
    current_url = resolve(request.path_info).url_name
    member = Member.objects.get(id=member_id)
    member_want_list = MemberWantlist.objects.get(member=member)
    members_collection = LibraryPlate.objects.filter(contributor=member).values_list('related_vinyl_plate__related_release__id', flat=True)

    context = {
        'member_want_list': member_want_list,
        'previous_url': current_url,
        'members_collection': members_collection,
        'move_and_swap_crates': move_and_swap_crates,
        'library': library,
        'cart': cart,
        'members': members
    }
    return render(request, 'cart.html', context)

# cart add item
def cart_add_item(request, library_id, release_id, previous_url):
    library = Library.objects.get(id=library_id)
    cart = Cart(request)
    vinyl_release = VinylRelease.objects.get(id=release_id)
    cart.add(vinyl_release=vinyl_release)
    context = {
        'library': library,
        'release': vinyl_release,
    }
    if 'release_compile' in previous_url:
        return render(request, 'return_to_release_compile.html', context)
    else:
        return render(request, 'return_to_vinyl_ordering.html', context)

# cart remove item
def cart_remove_item(request, library_id, release_id):
    library = Library.objects.get(id=library_id)
    cart = Cart(request)
    vinyl_release = VinylRelease.objects.get(id=release_id)
    cart.remove(vinyl_release=vinyl_release)
    context = {
        'library': library,
        'cart': cart
    }
    return render(request, 'return_to_vinyl_ordering.html', context)

# cart submission
def cart_submission(request, library_id, member_id):
    library = Library.objects.get(id=library_id)
    cart = Cart(request)
    if request.method == 'POST':
        member = request.POST['search_member']
        order = Order(library=library, member_id=member)
        order.save()
    else:
        member = Member.objects.get(id=member_id)
        order = Order(library=library, member=member)
        order.save()

    for item in cart:
        OrderItem.objects.create(order=order, vinyl_release=item['vinyl_release'], price=item['price'])

    cart.clear()

    request.session['order_id'] = order.id
    
    context = {
        'library': library,
        'cart': cart,
        'order': order
    }
    return render(request, 'return_to_member_order.html', context)

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

