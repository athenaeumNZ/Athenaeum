from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

import re

from django.urls import resolve

from management.models import Library, Crate, Member, VinylColour, VinylPlateSize, VinylCondition, VinylSleeveType, VinylReleaseType, CrateType
from musicDatabase.models import VinylPlate
from vinylLibrary.models import CrateIssue, LibraryCrate, LibraryPlate, SubCrate

import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File

def index(request):
    return render (request, 'index.html')

#region crates, sub crate adding and deleting ################
def crates(request, library_id, member_id):
    library = Library.objects.get(id=library_id)

    # pending crate
    pending_crate = SubCrate.objects.filter(
        sub_crate_id__icontains='Pending').get(
        master_library_crate__library=library)
    
    crate_plates = LibraryPlate.objects.filter(related_sub_crate=(pending_crate))
    pending_crate.plate_count = crate_plates.count()
    
    master_crates = Crate.objects.all()

    for master_crate in master_crates:
        if master_crate.crate_id == str(pending_crate.sub_crate_id)[:-4]:
            pending_crate.description = master_crate.description

    # member crates
    member = Member.objects.get(id=member_id)
    member_crates = SubCrate.objects.filter(sub_crate_id__icontains=(member.membership_number))

    for crate in member_crates:
        crate_plates = LibraryPlate.objects.filter(related_sub_crate=(crate))
        crate.plate_count = crate_plates.count()
    
    special_crates = ['To Library', 'On Order', 'Processing Order', 'Stockpile', 'Placing Order', 'Limbo']
    
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

    # to library crates
    to_library_crates = SubCrate.objects.filter(sub_crate_id__contains='To Library').exclude(sub_crate_id__contains='Library To Library')

    for crate in to_library_crates:
        crate_plates = LibraryPlate.objects.filter(related_sub_crate=(crate))
        crate.plate_count = crate_plates.count()

    pending_description = Crate.objects.filter(crate_id='Pending').values_list('description', flat=True)[0]

    to_library_crates.valid_crates = []
    for crate in to_library_crates:
        if crate.plate_count >= 1:
            to_library_crates.valid_crates.append(crate)

    # library to library crates
    library_to_library_crates = SubCrate.objects.filter(sub_crate_id__contains='Library to Library')

    for crate in library_to_library_crates:
        crate_plates = LibraryPlate.objects.filter(related_sub_crate=(crate))
        crate.plate_count = crate_plates.count()

    pending_description = Crate.objects.filter(crate_id='Pending').values_list('description', flat=True)[0]

    library_to_library_crates.valid_crates = []
    for crate in library_to_library_crates:
        if crate.plate_count >= 1:
            library_to_library_crates.valid_crates.append(crate)

    # library crates
    library_crates = LibraryCrate.objects.filter(
        library_id=library_id).exclude(
        related_crate__crate_id="Library to Library").exclude(
        related_crate__crate_id="Pending").exclude(
        related_crate__crate_id="Member")

    for crate in library_crates:
        crate.crate_plates = LibraryPlate.objects.filter(related_library_crate__exact=(crate))

    lc_s = LibraryCrate.objects.filter(library_id=library_id)
    l2l = 'Library to Library ' + str(library.name)[:3].upper()
    library.l2l_count = []
    for crate in lc_s:
        if crate.library_crate_id == l2l:
            library.l2l_count.append(crate)

    for crate in library_crates:
        crate.crate_sub_crates = SubCrate.objects.filter(master_library_crate=crate)


    # crates not in library
    cartes_to_exclude = [
        'Library to Library',
        'Limbo',
        'On Order',
        'Pending',
        'Processing Order',
        'Stockpile',
        'To Library',
        'Placing Order'
    ]
    
    crates_not_in_library = Crate.objects.all()
    for crate in cartes_to_exclude:
        crates_not_in_library = crates_not_in_library.exclude(crate_id__contains=(crate))
    
    libraries_existing_crates = LibraryCrate.objects.filter(library=library)
    lec_crate_ids = libraries_existing_crates.values_list('related_crate__crate_id', flat=True)

    for i in lec_crate_ids:
        crates_not_in_library = crates_not_in_library.exclude(crate_id__contains=(i))
    
    sale_sub_crates = SubCrate.objects.filter(sub_crate_id__contains='Sale Vinyl')

    context = {
        'library':library,
        'pending_crate': pending_crate,
        'member_crates': member_crates,
        'to_library_crates': to_library_crates,
        'sale_sub_crates': sale_sub_crates,
        'library_to_library_crates': library_to_library_crates,
        'library_crates': library_crates,
        'crates_not_in_library': crates_not_in_library,

        'pending_description': pending_description
    }
    return render(request,'crates.html', context)

def return_to_crates(request, library_id):
    library = Library.objects.get(id=library_id)

    context = {
        'library': library
    }
    return render(request,'return_to_crates.html', context)

'''need to update these searches'''
# library crates search
def library_crate_search_by_crate_id(request, library_id):
    query_library_crate_id = request.GET["query_library_crate_id"]
    library_crates = LibraryCrate.objects.exclude(related_crate__crate_id="PENDING").exclude(related_crate__crate_id="TRADE").filter(library_crate_id__icontains=query_library_crate_id)
    library = Library.objects.get(id=library_id)
    wantlist = WantlistCrate.objects.filter(library_id=library_id)
    tradelist = LibraryCrate.objects.filter(library_id=library_id, related_crate__crate_id="TRADE")
    pending = LibraryCrate.objects.filter(library_id=library_id, related_crate__crate_id="PENDING")
    context = {
        'library':library,
        'library_crates': library_crates,
        'wantlist': wantlist,
        'tradelist': tradelist,
        'pending': pending
    }
    return render(request,'crates.html', context)

def library_crate_search_by_crate_name(request, library_id):
    query_library_crate_name = request.GET["query_library_crate_name"]
    library_crates = LibraryCrate.objects.exclude(related_crate__crate_id="PENDING").exclude(related_crate__crate_id="TRADE").filter(related_crate__genre__icontains=query_library_crate_name)
    library = Library.objects.get(id=library_id)
    wantlist = WantlistCrate.objects.filter(library_id=library_id)
    tradelist = LibraryCrate.objects.filter(library_id=library_id, related_crate__crate_id="TRADE")
    pending = LibraryCrate.objects.filter(library_id=library_id, related_crate__crate_id="PENDING")
    context = {
        'library':library,
        'library_crates': library_crates,
        'wantlist': wantlist,
        'tradelist': tradelist,
        'pending': pending
    }
    return render(request,'crates.html', context)
''''''
# library crate add
def library_crate_add(request, library_id):
    library = Library.objects.get(id=library_id)

    cartes_to_exclude = [
        'Library to Library',
        'Limbo',
        'On Order',
        'Pending',
        'Processing Order',
        'Stockpile',
        'To Library',
        'Placing Order'
    ]
    
    crates = Crate.objects.all()
    for crate in cartes_to_exclude:
        crates = crates.exclude(crate_id__contains=(crate))
    
    libraries_existing_crates = LibraryCrate.objects.filter(library=library)
    lec_crate_ids = libraries_existing_crates.values_list('related_crate__crate_id', flat=True)

    for i in lec_crate_ids:
        crates = crates.exclude(crate_id__contains=(i))

    crate_types = CrateType.objects.all()
    context = {
        'library': library,
        'crates': crates,
        'crate_types': crate_types,
        'lec_crate_ids': lec_crate_ids,
    }
    return render(request, 'library_crate_add.html', context)

# library crate add submission
def library_crate_add_submission(request, library_id):
    if request.method == "POST":
        related_crate = request.POST['related_crate']
        crate_type = request.POST['crate_type']
        selected_crate = Crate.objects.get(crate_id = related_crate)
        crate_id = selected_crate.id
        library_id = request.POST['library_id']
        library_crate_id = request.POST['library_crate_id']
        obj = LibraryCrate(
            related_crate_id=crate_id, library_id=library_id, 
            library_crate_id=library_crate_id, crate_type=crate_type)
        obj.save()
        
        library = Library.objects.get(id=library_id)
        library_crates = LibraryCrate.objects.filter(library_id=library_id)
        context = {
            'library':library,
            'library_crates': library_crates
        }

        return render(request, 'return_to_crates.html', context)
    return redirect('/')

# library crate delete
def library_crate_delete(request, library_id, library_crate_id):
    library = Library.objects.get(id=library_id)
    crate = LibraryCrate.objects.get(id=library_crate_id)
    context = {
        'library': library,
        'crate': crate
    }
    return render(request, 'library_crate_delete.html', context)

# library crate delete submission
def library_crate_delete_submission(request, library_id, library_crate_id):
    library = Library.objects.get(id=library_id)
    crate = LibraryCrate.objects.get(id=library_crate_id)
    crate.delete()
    context = {
        'library':library,
    }
    return render(request, 'return_to_crates.html', context)

# sub crate add ---- This is on the crates page
def sub_crate_add(request, library_id, library_crate_id):
    library = Library.objects.get(id=library_id)
    library_crate = LibraryCrate.objects.get(id=library_crate_id)
    context = {
        'library':library,
        'library_crate': library_crate
    }
    return render(request,'sub_crate_add.html', context)

# sub crate add submission ---- This is on the crates page
def sub_crate_add_submission(request, library_id, library_crate_id):
    if request.method == "POST":
        master_library_crate = request.POST['master_library_crate']
        crate_index_start = request.POST['crate_index_start']
        crate_index_end = request.POST['crate_index_end']
        sub_crate_id = request.POST['sub_crate_id']
        obj = SubCrate(
            master_library_crate_id=master_library_crate, crate_index_start=crate_index_start,
            crate_index_end=crate_index_end, sub_crate_id=sub_crate_id)
        obj.save()

        def save_barcode(self, *args, **kwargs):
            COD128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            code = COD128((f'{self.sub_crate_id}' + ' ' + f'{self.master_library_crate.library}'), writer=ImageWriter()).write(rv)
            self.barcode.save((
                f'{self.master_library_crate.related_crate.genre}' + ' ' +
                f'{self.master_library_crate.related_crate.vibe}' + ' ' +
                f'{self.master_library_crate.related_crate.energy_level}' + ' ' +
                f'{self.crate_index_start}' + '-' +
                f'{self.crate_index_end}' + '.png')
                , File(rv), save=False)
            return self.save(*args, **kwargs)

        save_barcode(SubCrate.objects.get(id=obj.pk))

        library = Library.objects.get(id=library_id)
        library_crate = LibraryCrate.objects.filter(library_id=library_crate_id)
        context = {
            'library':library,
            'library_crate': library_crate
        }
        return render(request, 'return_to_crates.html', context)
    return redirect('/')

# sub crate delete ---- This is on the crates page
def sub_crate_delete(request, library_id, sub_crate_id, member_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    member = Member.objects.get(id=member_id)
    context = {
        'library':library,
        'sub_crate': sub_crate,
        'member': member,
    }
    return render(request,'sub_crate_delete.html', context)

# sub crate delete submission ---- This is on the crates page
def sub_crate_delete_submission(request, library_id, sub_crate_id, member_id):
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    scid = sub_crate.sub_crate_id
    sub_crate.delete()
    library = Library.objects.get(id=library_id)
    member = Member.objects.get(id=member_id)
    context = {
        'library':library,
        'member': member,
    }
    if member.membership_number == scid[:6]:
        return render(request, 'return_to_members_crates.html', context)
    else:
        return render(request, 'return_to_crates.html', context)

#endregion

#region issue crate ################
# issue crate
def issue_crate(request, library_id, sub_crate_id):
    sub_crate = SubCrate.objects.get(id=sub_crate_id)

    if sub_crate.crate_index_start == 'A':
        index_start = '0'
    else:
        index_start = sub_crate.crate_index_start
        
    crate_plates = LibraryPlate.objects.filter(
        related_library_crate=sub_crate.master_library_crate).filter(
        related_vinyl_plate__related_release__catalog_number__gte=(index_start)).filter(
        related_vinyl_plate__related_release__catalog_number__lte=(sub_crate.crate_index_end)) | LibraryPlate.objects.filter(
        related_library_crate=sub_crate.master_library_crate).filter(
        related_vinyl_plate__related_release__catalog_number__startswith=(sub_crate.crate_index_end)).order_by(
        'related_vinyl_plate')
    
    sub_crate.plate_count = crate_plates.count()
    sub_crate.save()

    library = Library.objects.get(id=library_id)
    members = Member.objects.all().filter(library_id=library_id)
    context = {
        'sub_crate': sub_crate,
        'library': library,
        'members': members
    }
    return render(request,'issue_crate.html', context)

# issue crate submission
def issue_crate_submission(request, library_id, sub_crate_id):
    if request.method == 'POST':
        member_id = request.POST['member_id']
        store = SubCrate.objects.filter(id=sub_crate_id)   
        def get_issue_status(sub_crate):
            if sub_crate.issued=="Available":
                sub_crate.issued="Issued"
                obj = CrateIssue(member_id=member_id, sub_crate_id=sub_crate_id)
                obj.save()
                sub_crate.save()
            else:
                messages.error(request," Crate already issued !!!")
        issue_status_list = list(set(map(get_issue_status, store)))
        library = Library.objects.get(id=library_id)
        sub_crate = SubCrate.objects.get(id=sub_crate_id)
        member = Member.objects.get(id=member_id)
        context = {
            'sub_crate': sub_crate,
            'library': library,
            'member': member
        }
        return render(request, 'return_to_crates.html', context)
    return redirect('/')

#endregion

#region library details ################
# library details
def library_details(request, library_id):
    library = Library.objects.get(id=library_id)
    plate_count = LibraryPlate.objects.filter(related_library_crate__library=library_id).count()
    context = {
        'library':library,
        'plate_count': plate_count,
    }
    return render(request,'library_details.html', context)

#endregion

#region return crate ################
# return crate
def return_crate(request, library_id, sub_crate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    crate_issue = CrateIssue.objects.filter(sub_crate_id=sub_crate_id).order_by('date_time_created').last()
    context = {
        'library': library,
        'sub_crate': sub_crate,
        'crate_issue': crate_issue
    }
    return render(request,'return_crate.html', context)

# return crate submission
def return_crate_submission(request, library_id, sub_crate_id):
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    if sub_crate.issued=="Issued":
        sub_crate.issued = "Available"
    sub_crate.save()

    crate_issue = CrateIssue.objects.filter(sub_crate_id=sub_crate_id).order_by('date_time_created').last()
    if crate_issue.status=="Issued":
        crate_issue.status = "Returned"
    crate_issue.save()

    library = Library.objects.get(id=library_id)
    library_crates = LibraryCrate.objects.filter(library_id=library_id)
    context = {
        'sub_crate': sub_crate,
        'library':library,
        'library_crates': library_crates
    }
    return render(request,'return_to_crates.html', context)

#endregion

#region sub crate and library plates ################
# library plate add ---- This is from sub crates
def library_plate_add(request, library_id, library_crate_id, sub_crate_id, vinyl_plate_id):
    library = Library.objects.get(id=library_id)
    library_crate = LibraryCrate.objects.get(id=library_crate_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    members = Member.objects.filter(library_id=library_id)
    vinyl_plate = VinylPlate.objects.get(id=vinyl_plate_id)

    colours = VinylColour.objects.all()
    sleeve_types = VinylSleeveType.objects.all()
    release_types = VinylReleaseType.objects.all()
    conditions = VinylCondition.objects.all()
    plate_sizes = VinylPlateSize.objects.all()


    context = {
        'library': library,
        'library_crate': library_crate,
        'members': members,
        'vinyl_plate': vinyl_plate,
        'sub_crate': sub_crate,

        'colours': colours,
        'sleeve_types': sleeve_types,
        'release_types': release_types,
        'conditions': conditions,
        'plate_sizes': plate_sizes
    }

    if len(Member.objects.filter(membership_number=sub_crate.sub_crate_id[:6])) >= 1:
        member = Member.objects.get(membership_number=sub_crate.sub_crate_id[:6])
        context["member"] = member

    return render(request, 'library_plate_add.html', context)

# library plate add submission ---- This is from sub crates 
def library_plate_add_submission(request, library_id, library_crate_id, sub_crate_id):
    if request.method == "POST":
        related_vinyl_plate = request.POST['related_vinyl_plate']
        related_library_crate = request.POST['related_library_crate']
        contributor = request.POST['contributor']
        cover = request.POST['cover']
        plate_size = request.POST['plate_size']
        release_type = request.POST['release_type']
        media_condition = request.POST['media_condition']
        vinyl_colour = request.POST['vinyl_colour']
        
        plate = LibraryPlate(
            related_vinyl_plate_id=related_vinyl_plate,
            related_library_crate_id=related_library_crate,
            related_sub_crate_id = sub_crate_id,
            contributor_id=contributor,
            cover=cover, 
            plate_size=plate_size,
            release_type=release_type, 
            media_condition=media_condition,
            vinyl_colour=vinyl_colour)
        plate.save()


        def save_barcode(self, *args, **kwargs):          # overriding save() 
            COD128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            code = COD128((f'{self.related_vinyl_plate}' + ' ' + f'{self.related_library_crate}' + ' ' + f'{self.contributor.membership_number}'), writer=ImageWriter()).write(rv)
            self.barcode.save(f'{self.related_vinyl_plate}.png', File(rv), save=False)
            return self.save(*args, **kwargs)

        save_barcode(LibraryPlate.objects.get(id=plate.pk))

        library = Library.objects.get(id=library_id)
        library_crate = LibraryCrate.objects.get(id=library_crate_id)
        sub_crate = SubCrate.objects.get(id=sub_crate_id)

        member = Member.objects.get(id=contributor)

        catalog_number_start = plate.related_vinyl_plate.related_release.catalog_number[:1]
        
        if sub_crate.master_library_crate.crate_type == 'Mix':
            if re.match(r'\d', catalog_number_start):
                catalog_number_start = 'A'
            mlc = LibraryCrate.objects.get(id=request.POST['related_library_crate'])
            sub_crates = SubCrate.objects.filter(master_library_crate=mlc)

            for i in sub_crates:
                if i.crate_index_start <= catalog_number_start:
                    if i.crate_index_end >= catalog_number_start:
                        plate.related_sub_crate = i
                        plate.save()

        context = {
            'library':library,
            'library_crate': library_crate,
            'sub_crate': sub_crate
        }
        return render(request, 'return_to_sub_crate.html', context)
    return redirect('/')

# library plate add select plate ---- This is from sub crates 
def library_plate_add_select_plate(request, library_id, library_crate_id, sub_crate_id):
    library = Library.objects.get(id=library_id)
    library_crate = LibraryCrate.objects.get(id=library_crate_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    members = Member.objects.all()
    vinyl_plates = VinylPlate.objects.all()
    colours = VinylColour.objects.all()

    p = Paginator(vinyl_plates, 50)
    page = request.GET.get('page')
    v_plates = p.get_page(page)
    nums = "a" * v_plates.paginator.num_pages

    context = {
        'nums': nums,
        'v_plates': v_plates,
        'library': library,
        'library_crate': library_crate,
        'members': members,
        'vinyl_plates': vinyl_plates,
        'colours': colours,
        'sub_crate': sub_crate
    }
    return render(request, 'library_plate_add_select_plate.html', context)

# library plate add select plate search ---- This is from sub crates 
def library_plate_add_select_plate_catalog_search(request, library_id, library_crate_id, sub_crate_id):
    library = Library.objects.get(id=library_id)
    library_crate = LibraryCrate.objects.get(id=library_crate_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    members = Member.objects.all()
    search_catalog = request.POST["search_catalog"]
    vinyl_plates = VinylPlate.objects.filter(related_release__catalog_number__icontains=search_catalog)
    colours = VinylColour.objects.all()
    
    p = Paginator(vinyl_plates, 50)
    page = request.GET.get('page')
    v_plates = p.get_page(page)
    nums = "a" * v_plates.paginator.num_pages

    context = {
        'nums': nums,
        'v_plates': v_plates,
        'library': library,
        'library_crate': library_crate,
        'members': members,
        'vinyl_plates': vinyl_plates,
        'colours': colours,
        'sub_crate': sub_crate
    }
    return render(request, 'library_plate_add_select_plate.html', context)

# library plate delete ---- This is from sub crates
def library_plate_delete(request, library_id, sub_crate_id, plate_id):
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library = Library.objects.get(id=library_id)
    library_plate = LibraryPlate.objects.get(id=plate_id)
    context = {
        'library': library,
        'library_plate': library_plate,
        'sub_crate': sub_crate
    }
    return render(request, 'library_plate_delete.html', context)

# library plate delete submission ---- This is from sub crates
def library_plate_delete_submission(request, library_id, sub_crate_id, plate_id):
    library_plate = LibraryPlate.objects.get(id=plate_id)
    library_plate.delete()
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    context = {
        'library':library,
        'library_plate': library_plate,
        'sub_crate': sub_crate
    }
    return render(request, 'return_to_sub_crate.html', context)

#library plate edit ---- This is from sub crates
def library_plate_edit(request, library_id, sub_crate_id, plate_id):
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library = Library.objects.get(id=library_id)
    library_plate = LibraryPlate.objects.get(id=plate_id)

    plate_sizes = VinylPlateSize.objects.all()
    release_types = VinylReleaseType.objects.all()
    vinyl_colours = VinylColour.objects.all()
    conditions = VinylCondition.objects.all()
    sleeve_types = VinylSleeveType.objects.all()

    context = {
        'library': library,
        'library_plate': library_plate,
        'sub_crate': sub_crate,

        'plate_sizes': plate_sizes,
        'release_types': release_types,
        'vinyl_colours': vinyl_colours,
        'conditions': conditions,
        'sleeve_types': sleeve_types
    }
    return render(request, 'library_plate_edit.html', context)

#library plate edit submission ---- This is from sub crates
def library_plate_edit_submission(request, library_id, sub_crate_id, plate_id):
    if request.method == "POST":
        library_plate = LibraryPlate.objects.get(id=plate_id)
        library_plate.cover = request.POST['cover']
        library_plate.media_condition = request.POST['media_condition']
        
        if request.POST['plate_size']:
            library_plate.plate_size = request.POST['plate_size']
        
        library_plate.save()
        if request.POST['cover'] != 'Choose...':
            library_plate.cover = request.POST['cover']
            library_plate.save()
        if request.POST['release_type'] != 'Choose...':
            library_plate.release_type = request.POST['release_type']
            library_plate.save()
        if request.POST['vinyl_colour'] != 'Choose...':
            library_plate.vinyl_colour = request.POST['vinyl_colour']
            library_plate.save()

        

        library = Library.objects.get(id=library_id)
        sub_crate = SubCrate.objects.get(id=sub_crate_id)
        member_id = library_plate.contributor.id
        context = {
            'library':library,
            'library_plate': library_plate,
            'sub_crate': sub_crate,
            'member_id': member_id
        }

        
        if 'Limbo' in sub_crate.sub_crate_id:
            return render(request, 'return_to_member_limbo_crate.html', context)
        else:
            return render(request, 'return_to_sub_crate.html', context)
    return redirect('/')

# library plate move
def library_plate_move(request, library_id, sub_crate_id, plate_id):
    library = Library.objects.get(id=library_id)
    library_crates = LibraryCrate.objects.filter(
        library_id=library_id).exclude(
        crate_type='Member')
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library_plate = LibraryPlate.objects.get(id=plate_id)
    
    context = {
        'library': library,
        'library_crates': library_crates,
        'sub_crate': sub_crate,
        'library_plate': library_plate,
    }
    return render(request,'library_plate_move.html', context)

# library plate move submission
def library_plate_move_submission(request, library_id, sub_crate_id, plate_id):
    if request.method == 'POST':
        library = Library.objects.get(id=library_id)
        sub_crate = SubCrate.objects.get(id=sub_crate_id)
        library_plate = LibraryPlate.objects.get(id=plate_id)

        library_plate.related_library_crate_id = request.POST['related_library_crate']
        library_plate.save()

        # find the correct sub crates
        catalog_number_start = library_plate.related_vinyl_plate.related_release.catalog_number[:1]
        
        if re.match(r'\d', catalog_number_start):
            catalog_number_start = 'A'
        mlc = LibraryCrate.objects.get(id=request.POST['related_library_crate'])
        sub_crates = SubCrate.objects.filter(master_library_crate=mlc)

        for i in sub_crates:
            if i.crate_index_start <= catalog_number_start:
                if i.crate_index_end >= catalog_number_start:
                    library_plate.related_sub_crate = i
                    library_plate.save()

        context = {
            'catalog_number_start': catalog_number_start,
            'library': library,
            'sub_crate': sub_crate,
            'library_plate': library_plate
        }
        return render(request, 'return_to_sub_crate.html', context)
    return redirect('/')

# library plate printing
def library_plate_printing_page(request, library_id, sub_crate_id, plate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    master_master_crate = Crate.objects.all()
    plate = LibraryPlate.objects.get(id=plate_id)

    if sub_crate.crate_type == 'Member':
       
        def save_barcode(self, *args, **kwargs):
            COD128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            code = COD128((f'{self.related_vinyl_plate}' + ' ' + f'{self.related_sub_crate.sub_crate_id}'), writer=ImageWriter()).write(rv)
            self.barcode.save(f'{self.related_vinyl_plate}.png', File(rv), save=False)
            return self.save(*args, **kwargs)

        save_barcode(plate)
    else:
        def save_barcode(self, *args, **kwargs):
            COD128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            code = COD128((f'{self.related_vinyl_plate}' + ' ' + f'{self.related_library_crate}' + ' ' + f'{self.contributor.membership_number}'), writer=ImageWriter()).write(rv)
            self.barcode.save(f'{self.related_vinyl_plate}.png', File(rv), save=False)
            return self.save(*args, **kwargs)

        save_barcode(plate)
    
    context = {
        'library': library,
        'sub_crate': sub_crate,
        'plate': plate,
        'master_master_crate': master_master_crate
    }
    return render(request,'library_plate_printing_page.html', context)

# library plate printing all
def library_plate_printing_all_page(request, library_id, sub_crate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    
    if sub_crate.crate_index_start == 'A':
        index_start = '0'
    else:
        index_start = sub_crate.crate_index_start

    crate_plates = LibraryPlate.objects.filter(
        related_library_crate=sub_crate.master_library_crate).filter(
        related_vinyl_plate__related_release__catalog_number__gte=(index_start)).filter(
        related_vinyl_plate__related_release__catalog_number__lte=(sub_crate.crate_index_end)) | LibraryPlate.objects.filter(
        related_library_crate=sub_crate.master_library_crate).filter(
        related_vinyl_plate__related_release__catalog_number__startswith=(sub_crate.crate_index_end)).order_by(
        'related_vinyl_plate')

    if sub_crate.crate_type == 'Member':
        crate_plates = LibraryPlate.objects.filter(related_sub_crate=sub_crate)

       
        def save_barcode(self, *args, **kwargs):
            COD128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            code = COD128((f'{self.related_vinyl_plate}' + ' ' + f'{self.related_sub_crate.sub_crate_id}'), writer=ImageWriter()).write(rv)
            self.barcode.save(f'{self.related_vinyl_plate}.png', File(rv), save=False)
            return self.save(*args, **kwargs)

        for plate in crate_plates:
            save_barcode(plate)

    else:

        if sub_crate.crate_index_start == 'A':
            index_start = '0'
        else:
            index_start = sub_crate.crate_index_start

        crate_plates = LibraryPlate.objects.filter(
            related_library_crate=sub_crate.master_library_crate).filter(
            related_vinyl_plate__related_release__catalog_number__gte=(index_start)).filter(
            related_vinyl_plate__related_release__catalog_number__lte=(sub_crate.crate_index_end)) | LibraryPlate.objects.filter(
            related_library_crate=sub_crate.master_library_crate).filter(
            related_vinyl_plate__related_release__catalog_number__startswith=(sub_crate.crate_index_end)).order_by(
            'related_vinyl_plate')
    
        def save_barcode(self, *args, **kwargs):
            COD128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            code = COD128((f'{self.related_vinyl_plate}' + ' ' + f'{self.related_library_crate}' + ' ' + f'{self.contributor.membership_number}'), writer=ImageWriter()).write(rv)
            self.barcode.save(f'{self.related_vinyl_plate}.png', File(rv), save=False)
            return self.save(*args, **kwargs)

        for plate in crate_plates:
            save_barcode(plate)

    def save_barcode(self, *args, **kwargs): 
        COD128 = barcode.get_barcode_class('code128')
        rv = BytesIO()
        code = COD128((f'{self.related_vinyl_plate}' + ' ' + f'{self.related_library_crate}' + ' ' + f'{self.contributor.membership_number}'), writer=ImageWriter()).write(rv)
        self.barcode.save(f'{self.related_vinyl_plate}.png', File(rv), save=False)
        return self.save(*args, **kwargs)



    context = {
        'library': library,
        'sub_crate': sub_crate,
        'crate_plates': crate_plates,
    }
    return render(request,'library_plate_printing_all_page.html', context)

# return to subcrate
def return_to_sub_crate(request, library_id, library_crate_id, sub_crate_id):
    library = Library.objects.get(id=library_id)
    library_crate = LibraryCrate.objects.get(id=library_crate_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)

    if sub_crate.crate_index_start == 'A':
        index_start = '0'
    else:
        index_start = sub_crate.crate_index_start

    crate_plates = LibraryPlate.objects.filter(
        related_library_crate=library_crate).filter(
        related_vinyl_plate__related_release__catalog_number__gte=(index_start)).filter(
        related_vinyl_plate__related_release__catalog_number__lte=(sub_crate.crate_index_end)) | LibraryPlate.objects.filter(
        related_library_crate=library_crate).filter(
        related_vinyl_plate__related_release__catalog_number__startswith=(sub_crate.crate_index_end)).order_by(
        'related_vinyl_plate')
    plate_count = crate_plates.count()

    context = {
        'library': library,
        'crate_plates': crate_plates,
        'library_crate': library_crate,
        'sub_crate': sub_crate,
        'plate_count': plate_count
    }
    return render(request,'return_to_sub_crate.html', context)

# sub crate
def sub_crate(request, library_id, sub_crate_id, member_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)

    member = Member.objects.get(id=member_id)

    if member.membership_number in sub_crate.sub_crate_id:
        crate_plates = LibraryPlate.objects.filter(related_sub_crate__exact=(sub_crate_id))
    elif 'Library to Library' in sub_crate.master_library_crate.library_crate_id:
        crate_plates = LibraryPlate.objects.filter(related_sub_crate_id=sub_crate)
    elif 'To Library' in sub_crate.sub_crate_id:
        crate_plates = LibraryPlate.objects.filter(related_sub_crate_id=sub_crate)
    else:
        if sub_crate.crate_index_start == 'A':
            index_start = '0'
        else:
            index_start = sub_crate.crate_index_start
        crate_plates = LibraryPlate.objects.filter(
            related_library_crate=sub_crate.master_library_crate).filter(
            related_vinyl_plate__related_release__catalog_number__gte=(index_start)).filter(
            related_vinyl_plate__related_release__catalog_number__lte=(sub_crate.crate_index_end)).filter(
            related_sub_crate=sub_crate) | LibraryPlate.objects.filter(
            related_library_crate=sub_crate.master_library_crate).filter(
            related_vinyl_plate__related_release__catalog_number__startswith=(sub_crate.crate_index_end)).filter(
            related_sub_crate=sub_crate).order_by(
            'related_vinyl_plate')

    plate_count = crate_plates.count()
    sub_crate.plate_count = plate_count
    sub_crate.save()
    track_crate_ids = crate_plates.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)
    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)

    current_url = resolve(request.path_info).url_name

    context = {
        'library': library,
        'crate_plates': crate_plates,
        'previous_url': current_url,
        'sub_crate': sub_crate,
        'plate_count': plate_count,
        'member': member,
        'track_crate_ids': track_crate_ids,
    }
    return render(request,'sub_crate.html', context)

# sub crate divider insert printing
def sub_crate_divider_insert_printing(request, library_id, sub_crate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    sub_crate.crate_id = str(sub_crate.sub_crate_id)[7:][:-4]
    member_id = sub_crate.sub_crate_id[:6]
    context = {
        'library':library,
        'sub_crate': sub_crate,
        'member_id': member_id
    }
    return render(request,'sub_crate_divider_insert_printing.html', context)

# sub crate edit
def sub_crate_edit(request, library_id, library_crate_id, sub_crate_id):
    library = Library.objects.get(id=library_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library_crate = LibraryCrate.objects.get(id=library_crate_id)

    if sub_crate.crate_type == 'Member' or sub_crate.crate_type == 'Admin':
        member = Member.objects.get(membership_number=sub_crate.sub_crate_id[:6])
    else:
        current_user = request.user
        member = current_user.member
    context = {
        'library':library,
        'sub_crate': sub_crate,
        'library_crate': library_crate,
        'member': member,
    }
    return render(request,'sub_crate_edit.html', context)

# dub crate edit submission
def sub_crate_edit_submission(request, library_id, library_crate_id, sub_crate_id):
    if request.method == "POST":
        sub_crate = SubCrate.objects.get(id=sub_crate_id)
        sub_crate.crate_index_start = request.POST['crate_index_start']
        sub_crate.crate_index_end = request.POST['crate_index_end']
        sub_crate.sub_crate_id = request.POST['sub_crate_id']
        sub_crate.save()

        library = Library.objects.get(id=library_id)
        library_crate = LibraryCrate.objects.get(id=library_crate_id)

        def save_barcode(self, *args, **kwargs):
            COD128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            code = COD128((f'{self.sub_crate_id}' + ' ' + f'{self.master_library_crate.library}'), writer=ImageWriter()).write(rv)
            self.barcode.save((
                f'{self.master_library_crate.related_crate.genre}' + ' ' +
                f'{self.master_library_crate.related_crate.vibe}' + ' ' +
                f'{self.master_library_crate.related_crate.energy_level}' + ' ' +
                f'{self.crate_index_start}' + '-' +
                f'{self.crate_index_end}' + '.png')
                , File(rv), save=False)
            return self.save(*args, **kwargs)

        save_barcode(sub_crate)

        if sub_crate.crate_index_start == 'A':
            index_start = '0'
        else:
            index_start = sub_crate.crate_index_start

        crate_plates = LibraryPlate.objects.filter(
            related_library_crate=sub_crate.master_library_crate).filter(
            related_vinyl_plate__related_release__catalog_number__gte=(index_start)).filter(
            related_vinyl_plate__related_release__catalog_number__lte=(sub_crate.crate_index_end)) | LibraryPlate.objects.filter(
            related_library_crate=sub_crate.master_library_crate).filter(
            related_vinyl_plate__related_release__catalog_number__startswith=(sub_crate.crate_index_end)).order_by(
            'related_vinyl_plate')
        
        for i in crate_plates:
            i.related_sub_crate = sub_crate
            i.save()

        context = {
            'library':library,
            'sub_crate': sub_crate,
            'library_crate': library_crate
        }
        return render(request, 'return_to_sub_crate.html', context)
    return redirect('/')

# sub crate search
def sub_crate_search(request, library_id, library_crate_id, sub_crate_id, member_id):
    library = Library.objects.get(id=library_id)
    library_crate = LibraryCrate.objects.get(id=library_crate_id)
    sub_crate = SubCrate.objects.get(id=sub_crate_id)

    member = Member.objects.get(id=member_id)

    if member.membership_number in sub_crate.sub_crate_id:
        crate_plates = LibraryPlate.objects.filter(related_member_crate__exact=(sub_crate_id))
    else:
        if sub_crate.crate_index_start == 'A':
            index_start = '0'
        else:
            index_start = sub_crate.crate_index_start
        crate_plates = LibraryPlate.objects.filter(
            related_library_crate=library_crate).filter(
            related_vinyl_plate__related_release__catalog_number__gte=(index_start)).filter(
            related_vinyl_plate__related_release__catalog_number__lte=(sub_crate.crate_index_end)) | LibraryPlate.objects.filter(
            related_library_crate=library_crate).filter(
            related_vinyl_plate__related_release__catalog_number__startswith=(sub_crate.crate_index_end)).order_by(
            'related_vinyl_plate')
    plate_count = crate_plates.count()

    track_crate_ids = crate_plates.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
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
        crate_plates = crate_plates.filter(related_vinyl_plate__related_vinyl_track__crate_id__exact=(search_track_crate_id)).distinct().order_by()
    if search_artist:
        crate_plates = crate_plates.filter(related_vinyl_plate__related_vinyl_track__artist__icontains=(search_artist)).distinct().order_by()   
    if search_label:
        crate_plates = crate_plates.filter(related_vinyl_plate__related_release__label__icontains=(search_label)).order_by()
    if search_catalog:
        crate_plates = crate_plates.filter(related_vinyl_plate__related_release__catalog_number__icontains=(search_catalog)).order_by()
    if search_release_year != '':
        crate_plates = crate_plates.filter(related_vinyl_plate__related_release__release_date__icontains=(search_release_year)).order_by()

    track_crate_ids = crate_plates.values_list('related_vinyl_plate__related_vinyl_track__crate_id', flat=True).distinct().order_by('related_vinyl_plate__related_vinyl_track__crate_id')
    track_crate_ids = list(track_crate_ids)
    if '?' in track_crate_ids:
        track_crate_ids.remove('?')
    if '-' in track_crate_ids:
        track_crate_ids.remove('-')
    if None in track_crate_ids:
        track_crate_ids.remove(None)

    context = {
        'library': library,
        'crate_plates': crate_plates,
        'library_crate': library_crate,
        'sub_crate': sub_crate,
        'plate_count': plate_count,

        'track_crate_ids': track_crate_ids,

        'search_track_crate_id': search_track_crate_id,
        'search_artist': search_artist,
        'search_label': search_label,
        'search_catalog': search_catalog,
        'search_release_year': search_release_year,

    }

    return render(request,'sub_crate.html', context)

#endregion

'''are trade crates still a thing?'''
# trade plate move
def trade_plate_move(request, library_id, sub_crate_id, plate_id):
    library = Library.objects.get(id=library_id)    
    sub_crate = SubCrate.objects.get(id=sub_crate_id)
    library_plate = LibraryPlate.objects.get(id=plate_id)
    trade_crates = LibraryCrate.objects.filter(crate_type='Pending')

    context = {
        'library': library,
        'sub_crate': sub_crate,
        'library_plate': library_plate,
        'trade_crates': trade_crates
    }
    return render(request,'trade_plate_move.html', context)

# trade plate move subission
def trade_plate_move_submission(request, library_id, sub_crate_id, plate_id):
    if request.method == 'POST':
        library = Library.objects.get(id=library_id)
        sub_crate = SubCrate.objects.get(id=sub_crate_id)
        library_plate = LibraryPlate.objects.get(id=plate_id)
        library_plate.related_library_crate_id = request.POST['related_library_crate']
        library_plate.save()
        
         # find the correct sub crates
        catalog_number_start = library_plate.related_vinyl_plate.related_release.catalog_number[:1]
        
        if re.match(r'\d', catalog_number_start):
            catalog_number_start = 'A'
        mlc = LibraryCrate.objects.get(id=request.POST['related_library_crate'])
        sub_crates = SubCrate.objects.filter(master_library_crate=mlc)

        for i in sub_crates:
            if i.crate_index_start <= catalog_number_start:
                if i.crate_index_end >= catalog_number_start:
                    library_plate.related_sub_crate = i
                    library_plate.save()
                    
        context = {
            'library': library,
            'sub_crate': sub_crate,
        }
        return render(request, 'return_to_sub_crate.html', context)
    return redirect('/')
