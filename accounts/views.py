from datetime import date, datetime, timedelta
from decimal import Decimal
from django.shortcuts import render
from django.urls import resolve
from accounts.models import Invoice, InvoiceItem, OrderRequestItem, PurchaseOrderRequest, PurchaseOrderRequestItem

from management.models import Library, Member, VinylCondition, VinylDistributor
from members.models import MemberPlate, MemberRelease, MemberReleaseStatusChoices
from musicDatabase.models import VinylPlate, VinylRelease, VinylTrack
from professionalServices.models import ProfessionalServicesInvoice
from vinylShop.models import StockItem


#region back orders. Needs to be looked over. Maybe the total value of items has a better way to be done.s
def distributors_back_orders(request, library_id):
    library = Library.objects.get(id=library_id)
    distributor = VinylDistributor.objects.get(id=request.POST['distributor_id'])

    ordered_items = OrderRequestItem.objects.filter(
        vinyl_release__distributor=distributor,
        ordered=True,
        stockpiled=False
        ).order_by(
            'vinyl_release__catalog_number')
    
    releases = []

    for i in ordered_items:
        if i.vinyl_release not in releases:
            releases.append(i.vinyl_release)

    estimated_value_NZD = 0
    for i in ordered_items:
        release = VinylRelease.objects.get(catalog_number=i.vinyl_release)
        estimated_value_NZD += release.cost_price_NZD * i.quantity

    estimated_value_NZD_with_shipping = estimated_value_NZD
    for i in ordered_items:
        estimated_value_NZD_with_shipping += 4 * i.quantity

    estimated_value_NZD_with_shipping_including_gst = round(Decimal(estimated_value_NZD_with_shipping) * Decimal(1.15), 2)

    estimated_value_distributors_currency = 0
    for i in ordered_items:
        release = VinylRelease.objects.get(catalog_number=i.vinyl_release)
        estimated_value_distributors_currency += release.cost_price * i.quantity

    for r in releases:
        r.quantity = 0
        for i in ordered_items:
            if i.vinyl_release == r:
                r.quantity += i.quantity

    today = date.today()
    shipment_date = datetime.today()+timedelta(days=7)

    ordered_items_for_weight = OrderRequestItem.objects.filter(
        vinyl_release__distributor=distributor).filter(
        ordered=True).filter(
        stockpiled=False).filter(
        paid=False).filter(
        vinyl_release__release_date__lte=shipment_date).order_by(
        'vinyl_release__catalog_number')
    
    total_weight = 0
    for i in ordered_items_for_weight:
        total_weight += i.weight_item

    total_weight = round(total_weight * Decimal(0.025), 2)
    
    context = {
        'library': library,
        'releases': releases,
        'distributor': distributor,
        'today': today,
        'shipment_date': shipment_date,
        'total_weight': total_weight,
        'estimated_value_NZD': estimated_value_NZD,
        'estimated_value_NZD_with_shipping': estimated_value_NZD_with_shipping,
        'estimated_value_NZD_with_shipping_including_gst': estimated_value_NZD_with_shipping_including_gst,
        'estimated_value_distributors_currency': estimated_value_distributors_currency,
    }

    return render(request,'distributors_back_orders.html', context)

def distributors_priority_orders(request, library_id, distributor_id):
    library = Library.objects.get(id=library_id)
    distributor = VinylDistributor.objects.get(id=distributor_id)

    ordered_items = OrderRequestItem.objects.filter(
        vinyl_release__distributor=distributor).filter(
        ordered=True).filter(
        stockpiled=False).filter(
        paid=False).filter(
        unavailable=False).filter(
        to_direct_shopping_invoice=False).order_by(
        'vinyl_release__catalog_number').exclude(order_request__member__user=library.librarian.id)
    
    releases = []

    for i in ordered_items:
        if i.vinyl_release not in releases:
            releases.append(i.vinyl_release)

    for r in releases:
        r.quantity = 0
        for i in ordered_items:
            if i.vinyl_release == r:
                r.quantity += i.quantity

    today = date.today()
    shipment_date = today+timedelta(days=5)

    ordered_items_for_weight = OrderRequestItem.objects.filter(
        vinyl_release__distributor=distributor).filter(
        ordered=True).filter(
        stockpiled=False).filter(
        paid=False).filter(
        vinyl_release__release_date__lte=shipment_date).order_by(
        'vinyl_release__catalog_number')
    
    total_weight = 0
    for i in ordered_items_for_weight:
        total_weight += i.weight_item

    total_weight = round(total_weight * Decimal(0.025), 2)

    context = {
        'library': library,
        'releases': releases,
        'distributor': distributor,
        'today': today,
        'shipment_date': shipment_date,
        'total_weight': total_weight,
    }

    return render(request,'distributors_priority_orders.html', context)

#endregion


#region dashboard

def dashboard(request, library_id):
    library = Library.objects.get(id=library_id)
    order_request_items = OrderRequestItem.objects.filter(delivered=False).order_by('member')
    distributors = VinylDistributor.objects.filter(active=True).order_by('name')
    
    #region distributors_with_unprocessed_purchase_order_requests
    distributors_with_unprocessed_purchase_order_requests = set()
    unordered_items = order_request_items.filter(ordered=False)
    for i in unordered_items:
        vinyl_release = VinylRelease.objects.get(catalog_number=i.vinyl_release)
        if vinyl_release.distributor not in distributors_with_unprocessed_purchase_order_requests and vinyl_release.distributor.active:
            distributors_with_unprocessed_purchase_order_requests.add(vinyl_release.distributor)
    #endregion
    
    #region members with current order request items
    members_with_current_order_request_items = set()
    for i in order_request_items:
        members_with_current_order_request_items.add(i.member)
    members_with_current_order_request_items = list(members_with_current_order_request_items)[1:]
    #endregion
    
    #region update order_request_items to [0]
    order_request_items = order_request_items[:0]
    #endregion
    
    #region query_order_by
    query_order_by = ['A-Z', 'Release Date', 'Ordered']
    #endregion
    
    invoices = Invoice.objects.all().filter(archived=False)
    members_all = Member.objects.filter(active=True)
    
    #region members with stockpile
    members_with_stockpile = []
    for i in members_all:
        order_request_is = OrderRequestItem.objects.filter(
            member=i,
            stockpiled=True,
            invoiced=False,
            to_become_shop_stock=False
        )
        if order_request_is.count() >= 1:
            members_with_stockpile.append(i)
    #endregion
    
    #region purchase order requests
    purchase_order_requests = []
    for i in PurchaseOrderRequest.objects.all():
        if not i.all_filled_or_unavailable:
            purchase_order_requests.append(i)
    #endregion
    
    current_url = resolve(request.path_info).url_name
    
    #region stock_items_not_updated_by_librarian
    stock_items_not_updated_by_library_shop = StockItem.objects.filter(
        library=library,
        added_by_member=True,
        updated_by_library_shop=False,
    )
    #endregion
    
    context = {
        'library': library,
        'order_request_items': order_request_items,
        'members_all': members_all,
        'members_with_stockpile': members_with_stockpile,
        'members_with_current_order_request_items': members_with_current_order_request_items,
        'query_order_by': query_order_by,
        'invoices': invoices,
        'distributors_with_unprocessed_purchase_order_requests': distributors_with_unprocessed_purchase_order_requests,
        'distributors': distributors,
        'previous_url': current_url,
        'purchase_order_requests': purchase_order_requests,
        'stock_items_not_updated_by_library_shop': stock_items_not_updated_by_library_shop,
    }
    
    return render(request,'dashboard.html', context)

def dashboard_search(request, library_id):
    library = Library.objects.get(id=library_id)
    order_request_items = OrderRequestItem.objects.filter(delivered=False).order_by('member')
    distributors = VinylDistributor.objects.filter(active=True).order_by('name')
    
    
    #region distributors_with_unprocessed_purchase_order_requests
    distributors_with_unprocessed_purchase_order_requests = set()
    unordered_items = order_request_items.filter(ordered=False)
    for i in unordered_items:
        vinyl_release = VinylRelease.objects.get(catalog_number=i.vinyl_release)
        if vinyl_release.distributor not in distributors_with_unprocessed_purchase_order_requests and vinyl_release.distributor.active:
            distributors_with_unprocessed_purchase_order_requests.add(vinyl_release.distributor)
    #endregion
    
    #region members with current order request items
    members_with_current_order_request_items = set()
    for i in order_request_items:
        members_with_current_order_request_items.add(i.member)
    members_with_current_order_request_items = list(members_with_current_order_request_items)[1:]
    #endregion
    
    #region update order_request_items to [0]
    order_request_items = order_request_items[:0]
    #endregion
    
    #region query_order_by
    query_order_by = ['A-Z', 'Release Date', 'Ordered']
    #endregion
    
    invoices = Invoice.objects.all().filter(archived=False)
    members_all = Member.objects.filter(active=True)
    
    #region members with stockpile
    members_with_stockpile = []
    for i in members_all:
        order_request_is = OrderRequestItem.objects.filter(
            member=i,
            stockpiled=True,
            invoiced=False,
            to_become_shop_stock=False
        )
        if order_request_is.count() >= 1:
            members_with_stockpile.append(i)
    #endregion
    
    #region purchase order requests
    purchase_order_requests = []
    for i in PurchaseOrderRequest.objects.all():
        if not i.all_filled_or_unavailable:
            purchase_order_requests.append(i)
    #endregion
    
    current_url = resolve(request.path_info).url_name
    
    #region stock_items_not_updated_by_librarian
    stock_items_not_updated_by_library_shop = StockItem.objects.filter(
        library=library,
        added_by_member=True,
        updated_by_library_shop=False,
    )
    #endregion
    
    context = {
        'library': library,
        'order_request_items': order_request_items,
        'members_all': members_all,
        'members_with_stockpile': members_with_stockpile,
        'members_with_current_order_request_items': members_with_current_order_request_items,
        'query_order_by': query_order_by,
        'invoices': invoices,
        'distributors_with_unprocessed_purchase_order_requests': distributors_with_unprocessed_purchase_order_requests,
        'distributors': distributors,
        'previous_url': current_url,
        'purchase_order_requests': purchase_order_requests,
        'stock_items_not_updated_by_library_shop': stock_items_not_updated_by_library_shop,
    }
    
    return render(request,'dashboard.html', context)

#region def dashboard_old(request, library_id):
    library = Library.objects.get(id=library_id)
    order_request_items = OrderRequestItem.objects.filter(delivered=False).order_by('member')
    distributors = VinylDistributor.objects.filter(active=True).order_by('name')
    #region distributors_with_unprocessed_purchase_order_requests
    distributors_with_unprocessed_purchase_order_requests = []
    unordered_items = order_request_items.filter(ordered=False)
    for i in unordered_items:
        vinyl_release = VinylRelease.objects.get(catalog_number=i.vinyl_release)
        if vinyl_release.distributor not in distributors_with_unprocessed_purchase_order_requests:
            if vinyl_release.distributor.active == True:
                distributors_with_unprocessed_purchase_order_requests.append(vinyl_release.distributor)
    #endregion
    #region members with current order request items
    members_with_current_order_request_items = []
    for i in order_request_items:
        member = i.member
        if member not in members_with_current_order_request_items:
            members_with_current_order_request_items.append(member)
    members_with_current_order_request_items = members_with_current_order_request_items[1:]
    #endregion
    #region update order_request_items to [0]
    order_request_items = order_request_items[:0]
    #endregion
    #region query_order_by
    query_order_by = [
        'A-Z',
        'Release Date',
        'Ordered'
    ]
    #endregion
    invoices = Invoice.objects.all().filter(archived=False)
    members_all = Member.objects.filter(active=True)
    #region members with stockpile
    members_with_stockpile = []
    for i in members_all:
        member = i
        order_request_is = OrderRequestItem.objects.filter(
        member = member,
        stockpiled = True,
        invoiced = False,
        to_become_shop_stock = False
        )
        if len(order_request_is) >= 1:
            members_with_stockpile.append(member)
    #endregion
    #region purchase order requests
    p_o_requests = PurchaseOrderRequest.objects.all()
    purchase_order_requests = []
    for i in p_o_requests:
        if i.all_filled_or_unavailable == False:
            purchase_order_requests.append(i)
    #endregion
    current_url = resolve(request.path_info).url_name
    #region stock_items_not_updated_by_librarian
    stock_items_not_updated_by_library_shop = StockItem.objects.filter(
        library=library,
        added_by_member=True,
        updated_by_library_shop=False,
        )
    #endregion
    
    #region utils
    '''
    labels = [
    ]
    for i in labels:
        change_label_distributor(i, 'UES', 'NKD')
    '''
    #endregion
    context = {
        'library': library,
        'order_request_items': order_request_items,
        'members_all': members_all,
        'members_with_stockpile': members_with_stockpile,
        'members_with_current_order_request_items': members_with_current_order_request_items,
        'query_order_by': query_order_by,
        'invoices': invoices,
        'distributors_with_unprocessed_purchase_order_requests': distributors_with_unprocessed_purchase_order_requests,
        'distributors': distributors,
        'previous_url': current_url,

        'purchase_order_requests': purchase_order_requests,

        'stock_items_not_updated_by_library_shop': stock_items_not_updated_by_library_shop,

    }
    # update_stock_levels_all(library_id)
    return render(request,'dashboard.html', context)
#endregion

def dashboard_search(request, library_id):
    library = Library.objects.get(id=library_id)
    order_request_items = OrderRequestItem.objects.filter(delivered=False).order_by('member')
    distributors = VinylDistributor.objects.filter(active=True).order_by('name')

    #region distributors_with_unprocessed_purchase_order_requests
    distributors_with_unprocessed_purchase_order_requests = set()
    unordered_items = order_request_items.filter(ordered=False)
    for i in unordered_items:
        vinyl_release = VinylRelease.objects.get(catalog_number=i.vinyl_release)
        if vinyl_release.distributor not in distributors_with_unprocessed_purchase_order_requests and vinyl_release.distributor.active:
            distributors_with_unprocessed_purchase_order_requests.add(vinyl_release.distributor)
    #endregion
    
    #region members with current order request items
    members_with_current_order_request_items = set()
    for i in order_request_items:
        members_with_current_order_request_items.add(i.member)
    members_with_current_order_request_items = list(members_with_current_order_request_items)[1:]
    #endregion
    
    #region search fields
    search_catalog = request.POST['search_catalog']
    search_member = request.POST['search_member']
    search_title = request.POST['search_title']
    search_label = request.POST['search_label']
    search_artist = request.POST['search_artist']
    search_distributor = request.POST['search_distributor']

    if search_catalog != 'Catalog...':
        order_request_items = order_request_items.filter(vinyl_release__catalog_number__icontains=(search_catalog))
    if search_member != 'Member...':
        order_request_items = order_request_items.filter(member__membership_number__icontains=(search_member))
    if search_title != 'Title...':
        order_request_items = order_request_items.filter(vinyl_release__release_title__icontains=(search_title))
    if search_label != 'Label...':
        order_request_items = order_request_items.filter(vinyl_release__label__icontains=(search_label))
    if search_artist != 'Artist...':
        order_request_items = order_request_items.filter(vinyl_release__artist__icontains=(search_artist))
    if search_distributor != 'Dist...':
        order_request_items = order_request_items.filter(vinyl_release__distributor__distributor_code__icontains=(search_distributor))
    #endregion
    
    #region query order by
    search_order_by = request.POST['search_order_by']
    query_order_by = ['A-Z', 'Release Date', 'Ordered']

    if search_order_by == 'A-Z':
        order_request_items = order_request_items.order_by('vinyl_release__catalog_number')
    elif search_order_by == 'Release Date':
        order_request_items = order_request_items.order_by('vinyl_release__release_date')
    else:
        order_request_items = order_request_items.order_by('created')
    #endregion

    invoices = Invoice.objects.all().filter(archived=False)
    members_all = Member.objects.filter(active=True)
    
    #region members with stockpile
    members_with_stockpile = []
    for i in members_all:
        order_request_is = OrderRequestItem.objects.filter(
            member=i,
            stockpiled=True,
            invoiced=False,
            to_become_shop_stock=False
        )
        if order_request_is.count() >= 1:
            members_with_stockpile.append(i)
    #endregion
    
    #region purchase order requests
    purchase_order_requests = []
    for i in PurchaseOrderRequest.objects.all():
        if not i.all_filled_or_unavailable:
            purchase_order_requests.append(i)
    #endregion
    
    current_url = resolve(request.path_info).url_name

    #region order_request_items_to_stockpile & order_request_items_to_add_as_stock
    order_request_items_ids = []
    for i in order_request_items:
        if i.stockpiled != True:
            order_request_items_ids.append(i.pk)

    if order_request_items_ids == []:
        order_request_items_ids = None
    else:
        order_request_items_ids = str(order_request_items_ids)
        order_request_items_ids = order_request_items_ids[1:]
        order_request_items_ids = order_request_items_ids[:-1]

    if order_request_items_ids != None:
        order_request_items_to_stockpile = OrderRequestItem.objects.filter(id__in=str(order_request_items_ids).split(", "), to_become_shop_stock=False)
        order_request_items_to_add_as_stock = OrderRequestItem.objects.filter(id__in=str(order_request_items_ids).split(", "), to_become_shop_stock=True)
    else:
        order_request_items_to_stockpile = None
        order_request_items_to_add_as_stock = None
    #endregion

    #region search_member
    search_member_a = ''
    search_member_b = ''
    if search_member != 'Member...':
        member = Member.objects.get(membership_number=search_member)
        search_member_a = str(member.membership_number)
        search_member_b = str(member.user.first_name) + ' ' + str(member.user.last_name[:1]) + '.'
        members_with_current_order_request_items.remove(member)
    #endregion
    
    #region stock_items_not_updated_by_librarian
    stock_items_not_updated_by_library_shop = StockItem.objects.filter(
        library=library,
        added_by_member=True,
        updated_by_library_shop=False,
        )
    #endregion
    
    context = {
        'library': library,
        'order_request_items': order_request_items,
        'order_request_items_ids': order_request_items_ids,
        'order_request_items_to_stockpile': order_request_items_to_stockpile,
        'order_request_items_to_add_as_stock': order_request_items_to_add_as_stock,
        'members_all': members_all,
        'members_with_stockpile': members_with_stockpile,
        'members_with_current_order_request_items': members_with_current_order_request_items,
        'search_catalog': search_catalog,
        'search_member': search_member,
        'search_member_a': search_member_a,
        'search_member_b': search_member_b,
        'search_title': search_title,
        'search_label': search_label,
        'search_artist': search_artist,
        'search_order_by': search_order_by,
        'search_distributor': search_distributor,
        'query_order_by': query_order_by,
        'invoices': invoices,
        'distributors': distributors,
        'distributors_with_unprocessed_purchase_order_requests': distributors_with_unprocessed_purchase_order_requests,
        'previous_url': current_url,
        'purchase_order_requests': purchase_order_requests,
        'stock_items_not_updated_by_library_shop': stock_items_not_updated_by_library_shop,
    }

    return render(request,'dashboard.html', context)

def return_to_dashboard(request, library_id): # unused I think
    library = Library.objects.get(id=library_id)

    context = {
        'library': library,
    }

    return render(request,'dashboard.html', context)

#endregion


#region invoices


def invoice(request, library_id, invoice_id): #final
    library = Library.objects.get(id=library_id)
    invoice = Invoice.objects.get(id=invoice_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    
    context = {
        'library': library,
        'invoice': invoice,
        'invoice_items': invoice_items,
    }

    return render(request,'invoice.html', context)


def invoice_archive_submission(request, library_id, invoice_id): #final
    library = Library.objects.get(id=library_id)
    invoice = Invoice.objects.get(id=invoice_id)
    
    invoice.archived = True
    invoice.save()


    context = {
        'library': library,
    }

    return render(request,'return_to_dashboard.html', context)


def invoice_member_archive_submission(request, library_id, invoice_id): #final
    library = Library.objects.get(id=library_id)
    invoice = Invoice.objects.get(id=invoice_id)
    
    invoice.member_archived = True
    invoice.save()

    context = {
        'library': library,
        'member': invoice.member,
    }

    return render(request,'return_to_member_dashboard.html', context)


def invoice_create_submission(request, library_id, member_id): #needs to be updated and needs to include courier invoice details.
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    order_request_items = OrderRequestItem.objects.filter(
        member = member,
        library = library,
        hidden_from_member = False,
        unavailable = False,
        stockpiled = True,
        invoiced = False,
    )
    invoice_weight = float(request.POST['invoice_weight'])

    invoice_sub_total = float(request.POST['invoice_sub_total_excl_shipping'])
    invoice_gst = invoice_sub_total / 100 * 15
    shipping = str(request.POST['shipping']).split(',')
    invoice_shipping_type = shipping[0]
    invoice_shipping_cost = float(shipping[1])
    invoice_total_gst = invoice_gst + (invoice_shipping_cost / 115 * 15 )
    invoice_total = round(invoice_sub_total + invoice_gst + invoice_shipping_cost, 2)

    this_invoice = Invoice(
        member = member,
        library = library,
        invoice_weight = invoice_weight,
        invoice_shipping_type = invoice_shipping_type,
        invoice_shipping_cost = invoice_shipping_cost,
        invoice_sub_total = invoice_sub_total,
        invoice_gst = invoice_gst,
        invoice_total_gst = invoice_total_gst,
        invoice_total = invoice_total,
    )
    this_invoice.save()

    for i in order_request_items:
        invoice_item = InvoiceItem(
            order_request_item = i,
            invoice = this_invoice,
            invoiced_quantity = i.quantity,
            invoiced_sale_price = i.sale_price,
        )
        invoice_item.save()
        if invoice_item.invoiced_quantity != None and invoice_item.invoiced_sale_price != None:
            invoice_item.invoiced_sub_total = invoice_item.invoiced_quantity * invoice_item.invoiced_sale_price
            invoice_item.save()
        i.invoiced = True
        i.save()

    context = {
        'library': library,
        'invoice': this_invoice,
    }

    return render(request,'return_to_invoice.html', context)


def invoice_use_credit_submission(request, library_id, invoice_id): #draft
    library = Library.objects.get(id=library_id)
    invoice = Invoice.objects.get(id=invoice_id)
    invoice_total = invoice.invoice_total
    member = invoice.member
    member_account_credit = member.account_credit

    if member_account_credit <= invoice_total:
        invoice.invoice_discount_amount = member_account_credit
        member.account_credit = Decimal(0.00)
        invoice.save()
        member.save()
    else:
        member.account_credit = member_account_credit - invoice_total
        invoice.invoice_discount_amount = invoice_total
        invoice.invoice_total = Decimal(0.00)
        invoice.save()
        member.save()

    context = {
        'library': library,
        'invoice': invoice,
    }

    return render(request,'return_to_invoice.html', context)


def invoice_payment_cleared_submission(request, library_id, invoice_id): #final
    
    library = Library.objects.get(id=library_id)
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.paid = True
    invoice.save()
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    for i in invoice_items:
        i.order_request_item.paid = True
        i.order_request_item.save()

    context = {
        'library': library,
        'invoice': invoice,
    }
    
    return render(request,'return_to_dashboard.html', context)


def invoice_member_has_payed_submission(request, library_id, invoice_id): #final
    library = Library.objects.get(id=library_id)
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.member_has_made_payment = True
    invoice.save()
    '''Moved create member release and plates to shopping cart from plate sorter submission
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    in_coming = MemberReleaseStatusChoices.objects.get(status='In Coming')
    for i in invoice_items:
        order_request_item = i.order_request_item
        vinyl_release = i.order_request_item.vinyl_release
        if len(MemberRelease.objects.filter(order_request_item=order_request_item)) >= 1:
            existing_member_release_order_request_item = MemberRelease.objects.get(
                order_request_item=order_request_item)
            existing_member_release_order_request_item.status = in_coming
            existing_member_release_order_request_item.save()
        else:
            existing_member_release_order_request_item = None

        if existing_member_release_order_request_item == None:
            in_want_list = MemberReleaseStatusChoices.objects.get(status='In Want List')
            if len(MemberRelease.objects.filter(member=invoice.member, vinyl_release=vinyl_release, status=in_want_list)) >= 1:
                want_list_member_release = MemberRelease.objects.get(
                    member=invoice.member,
                    vinyl_release=vinyl_release,
                    status=in_want_list,
                )
                want_list_member_release.status = in_coming
                want_list_member_release.save()
            else:
                new_member_release = MemberRelease(
                    member = order_request_item.member,
                    vinyl_release = order_request_item.vinyl_release,
                    order_request_item = order_request_item,
                    status = in_coming,
                )
                new_member_release.save()
                vinyl_plates = VinylPlate.objects.filter(related_release=vinyl_release) # need to update to vinyl_release=vinyl_release
                vinyl_condition = VinylCondition.objects.get(condition='M')
                for k in vinyl_plates:
                    new_member_plate = MemberPlate(
                        member=invoice.member,
                        member_release=new_member_release,
                        vinyl_plate=k,
                        vinyl_condition=vinyl_condition,
                    )
                    new_member_plate.save()
    '''
    context = {
        'library': library,
        'member': invoice.member,
    }
    return render(request,'return_to_member_dashboard.html', context)


def invoice_member_has_received_all_plates_submission(request, library_id, invoice_id): #final

    library = Library.objects.get(id=library_id)
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.member_has_received_all_plates = True
    invoice.save()
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)

    for i in invoice_items:
        order_request_item = OrderRequestItem.objects.get(id=i.order_request_item.pk)
        order_request_item.delivered = True
        order_request_item.save()
        if len(MemberRelease.objects.filter(order_request_item=order_request_item)) == 1:
            member_release = MemberRelease.objects.get(order_request_item=order_request_item)
            in_collection = MemberReleaseStatusChoices.objects.get(status='In Collection')
            member_release.status = in_collection
            member_release.save()

    context = {
        'library': library,
        'member': invoice.member,
    }

    return render(request,'return_to_member_dashboard.html', context)


def return_to_invoice(request, library_id, invoice_id): #final
    library = Library.objects.get(id=library_id)
    invoice = Invoice.objects.get(id=invoice_id)

    context = {
        'library': library,
        'invoice': invoice,
    }

    return render(request,'return_to_invoice.html', context)


#endregion


#region order request items. All needs to be updated

def order_request_items_stockpile_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    if 'order_request_items_ids' in request.POST:
        order_request_items_ids = str(request.POST['order_request_items_ids'])
        order_request_items = OrderRequestItem.objects.filter(id__in=order_request_items_ids.split(", "))
    else:
        order_request_items = OrderRequestItem.objects.filter(id=request.POST['order_request_item_id'])
        
    for i in order_request_items:
        if i.to_become_shop_stock == True:
            i.stockpiled = True
            i.invoiced = True
            i.paid = True
            i.delivered = True
            i.save()
            stock_item = StockItem.objects.get(id=i.stock_item.pk)
            if stock_item.quantity == 0:
                stock_item.status = 2
            stock_item.quantity += i.quantity
            stock_item.quantity_incoming -= i.quantity
            stock_item.has_an_outer_sleeve = True
            stock_item.save()
        else:
            i.stockpiled = True
            i.save()
    context = {
        'library': library,
    }
    return render(request, 'return_to_dashboard.html', context)

def order_request_item_delete_submission(request, library_id, order_request_item_id):
    library = Library.objects.get(id=library_id)
    order_request_item = OrderRequestItem.objects.get(id=order_request_item_id)
    if order_request_item.to_become_shop_stock == True:
        if order_request_item.stock_item != None:
            stock_item = order_request_item.stock_item
            stock_item.quantity_incoming = stock_item.quantity_incoming - order_request_item.quantity
            stock_item.quantity_plus_quantity_incoming_stock = stock_item.quantity_plus_quantity_incoming_stock - order_request_item.quantity
            stock_item.save()
    if order_request_item.stock_item != None:
        stock_item = order_request_item.stock_item
    else:
        stock_item = None
    vinyl_release = order_request_item.vinyl_release
    order_request_item.delete()
    context = {
        'library': library,
        'stock_item': stock_item,
    }
    if context['stock_item'] != None:
        context['release'] = vinyl_release
        return render(request, 'stock_item_add_edit.html', context)
    else:
        return render(request, 'return_to_dashboard.html', context)

def order_request_item_order_submission(request, library_id, order_request_item_id):
    library = Library.objects.get(id=library_id)
    order_request_item = OrderRequestItem.objects.get(id=order_request_item_id)
    order_request_item.ordered = True
    if order_request_item.to_become_shop_stock == True:
        stock_item = order_request_item.stock_item
        if stock_item != None:
            if stock_item.quantity == 0:
                stock_item.status = 1
                stock_item.save()
    order_request_item.save()


    context = {
        'library': library,
    }

    return render(request, 'return_to_order_request.html', context)

def order_request_item_split(request, library_id, order_request_item_id):
    library = Library.objects.get(id=library_id)
    order_request_item = OrderRequestItem.objects.get(id=order_request_item_id)
    context = {
        'library': library,
        'order_request_item': order_request_item,
    }
    return render(request, 'order_request_item_split.html', context)

def order_request_item_split_submission(request, library_id, order_request_item_id):
    library = Library.objects.get(id=library_id)
    split_amount = request.POST['split_amount']
    order_request_item_a = OrderRequestItem.objects.get(id=order_request_item_id)
    order_request_item_a.quantity = int(order_request_item_a.quantity) - int(split_amount)
    order_request_item_a.save()

    order_request_item_b = order_request_item_a
    order_request_item_b.pk = None
    order_request_item_b.quantity = split_amount
    order_request_item_b.save()

    context = {
        'library': library,
    }

    return render(request, 'return_to_dashboard.html', context)

''' UNUSED '''
def order_request_item_stockpiled_submission(request, library_id, order_request_id, order_request_item_id, previous_url):
    library = Library.objects.get(id=library_id)
    order_request_item = OrderRequestItem.objects.get(id=order_request_item_id)
    order_request_item.stockpiled = True
    order_request_item.save()

    order_request = OrderRequest.objects.get(id=order_request_id)

    context = {
        'library': library,
        'order_request': order_request,
        'previous_url': previous_url,
    }

    if 'dashboard' in previous_url:
        return render(request, 'return_to_dashboard.html', context)
    else:
        return render(request, 'return_to_order_request.html', context)
''' UNUSED '''

def order_request_item_update(request, library_id, order_request_item_id):
    library = Library.objects.get(id=library_id)
    order_request_item = OrderRequestItem.objects.get(id=order_request_item_id)

    context = {
        'library': library,
        'order_request_item': order_request_item,
    }
    return render(request, 'order_request_item_update.html', context)

def order_request_item_update_submission(request, library_id, order_request_item_id):
    library = Library.objects.get(id=library_id)
    order_request_item = OrderRequestItem.objects.get(id=order_request_item_id)
    old_quantity = order_request_item.quantity
    new_quantity = int(str(request.POST['quantity']).replace("'", ""))
    order_request_item.quantity = request.POST['quantity']
    order_request_item.save()

    if order_request_item.to_become_shop_stock == True:
        if order_request_item.stock_item != None:
            stock_item = order_request_item.stock_item
            stock_item.quantity_incoming = stock_item.quantity_incoming - old_quantity + new_quantity
            stock_item.quantity_plus_quantity_incoming_stock = stock_item.quantity_plus_quantity_incoming_stock - old_quantity + new_quantity
            stock_item.save()

    context = {
        'library': library,
    }
    return render(request, 'return_to_dashboard.html', context)
    
#endregion


#region purchase order requests. Needs to be looked over

def purchase_order_request_template(request, library_id):
    library = Library.objects.get(id=library_id)
    distributor = VinylDistributor.objects.get(id=request.POST['distributor_id'])

    un_ordered_items = OrderRequestItem.objects.filter(
        vinyl_release__distributor=distributor).filter(
        ordered=False).filter(
        shop_purchase=False).order_by(
        'vinyl_release__catalog_number')
    
    releases = []

    for i in un_ordered_items:
        if i.vinyl_release not in releases:
            releases.append(i.vinyl_release)

    for r in releases:
        r.quantity = 0
        for i in un_ordered_items:
            if i.vinyl_release == r:
                r.quantity += i.quantity

    context = {
        'library': library,
        'distributor': distributor,
        'releases': releases,
    }

    return render(request, 'purchase_order_request_template.html', context)

def purchase_order_request(request, library_id, purchase_order_request_id):
    library = Library.objects.get(id=library_id)
    purchase_order_request = PurchaseOrderRequest.objects.get(id=purchase_order_request_id)
    purchase_order_request_items = PurchaseOrderRequestItem.objects.filter(
        purchase_order_request_id=purchase_order_request_id).order_by('vinyl_release__catalog_number')

    context = {
        'library': library,
        'purchase_order_request': purchase_order_request,
        'purchase_order_request_items': purchase_order_request_items,
    }

    return render(request,'purchase_order_request.html', context)

def purchase_order_request_item_edit(request, library_id, purchase_order_request_id, purchase_order_request_item_id):
    library = Library.objects.get(id=library_id)
    purchase_order_request_item = PurchaseOrderRequestItem.objects.get(
        id=purchase_order_request_item_id)
    order_request_items = OrderRequestItem.objects.filter(
        purchase_order_request_item=purchase_order_request_item)

    purchase_order_request = PurchaseOrderRequest.objects.get(id=purchase_order_request_id)

    context = {
        'library': library,
        'purchase_order_request_item': purchase_order_request_item,
        'order_request_items': order_request_items,
        'purchase_order_request': purchase_order_request,
    }

    return render(request, 'purchase_order_request_item_edit.html', context)

def purchase_order_request_item_edit_submission(request, library_id, purchase_order_request_id, purchase_order_request_item_id):
    library = Library.objects.get(id=library_id)
    purchase_order_request_item = PurchaseOrderRequestItem.objects.get(
        id=purchase_order_request_item_id)
    order_request_items = OrderRequestItem.objects.filter(
        purchase_order_request_item=purchase_order_request_item)
    
    purchase_order_request_item.filled = True
    purchase_order_request_item.save()

    purchase_order_request = PurchaseOrderRequest.objects.get(id=purchase_order_request_id)

    context = {
        'library': library,
        'purchase_order_request_item': purchase_order_request_item,
        'order_request_items': order_request_items,
        'purchase_order_request': purchase_order_request,
    }

    return render(request, 'purchase_order_request_item_edit.html', context)

def purchase_order_request_item_filled_submission(request, library_id, purchase_order_request_id, purchase_order_request_item_id):
    library = Library.objects.get(id=library_id)
    purchase_order_request_item = PurchaseOrderRequestItem.objects.get(
        id=purchase_order_request_item_id)
    purchase_order_request_item.filled = True
    purchase_order_request_item.save()

    purchase_order_request = PurchaseOrderRequest.objects.get(id=purchase_order_request_id)

    context = {
        'library': library,
        'purchase_order_request': purchase_order_request,
    }

    return render(request, 'return_to_purchase_order_request.html', context)

def purchase_order_request_items_filled_submission(request, library_id, purchase_order_request_id):
    library = Library.objects.get(id=library_id)
    purchase_order_request = PurchaseOrderRequest.objects.get(id=purchase_order_request_id)
    purchase_order_request_items = PurchaseOrderRequestItem.objects.filter(
        purchase_order_request=purchase_order_request)
    
    for i in purchase_order_request_items:
        i.filled = True
        i.save()

    context = {
        'library': library,
        'purchase_order_request': purchase_order_request,
    }

    return render(request, 'return_to_purchase_order_request.html', context)

def purchase_order_request_submission(request, library_id, distributor_id):
    library = Library.objects.get(id=library_id)

    purchase_order_request = PurchaseOrderRequest(
        library = library,
        distributor_id = distributor_id,
        )
    purchase_order_request.save()

    un_ordered_items = OrderRequestItem.objects.filter(
        vinyl_release__distributor__id=distributor_id).filter(
        ordered=False,)
    
    releases = []

    for i in un_ordered_items:
        if i.vinyl_release not in releases:
            releases.append(i.vinyl_release)

    for r in releases:
        purchase_order_request_item = PurchaseOrderRequestItem(
        purchase_order_request = purchase_order_request,
        vinyl_release_id = r.pk,
        )
        purchase_order_request_item.save()

        for i in un_ordered_items:
            if i.vinyl_release == purchase_order_request_item.vinyl_release:
                i.purchase_order_request_item = purchase_order_request_item
                i.ordered = True
                i.save()

    context = {
        'library': library,
        'purchase_order_request': purchase_order_request
    }

    return render(request, 'return_to_purchase_order_request.html', context)

def return_to_purchase_order_request(request, library_id, purchase_order_request_id):
    library = Library.objects.get(id=library_id)
    purchase_order_request = PurchaseOrderRequest.objects.get(id=purchase_order_request_id)
    
    context = {
        'library': library,
        'purchase_order_request': purchase_order_request,
    }

    return render(request, 'return_to_purchase_order_request.html', context)

#endregion