from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout

import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files import File

from choices.models import Genre
from management.models import Library, Crate, Vibe, EnergyLevel, CrateType
from vinylLibrary.models import LibraryCrate, SubCrate
from django.core.paginator import Paginator

############## crate database ##############
# crate add
def crate_add(request, library_id):
    library = Library.objects.get(id=library_id)

    genres = Genre.objects.all()
    vibes = Vibe.objects.all()
    energy_levels = EnergyLevel.objects.all()
    crate_types = CrateType.objects.all()

    context = {
        'library': library,

        'genres': genres,
        'vibes': vibes,
        'energy_levels': energy_levels,
        'crate_types': crate_types
    }
    return render(request,'crate_add.html', context)

# crate add submission
def crate_add_submission(request, library_id):
    library = Library.objects.get(id=library_id)
    if request.method == 'POST' and 'FILES':
        genre = request.POST['genre']
        vibe = request.POST['vibe']
        energy_level = request.POST['energy_level']
        description = request.POST['description']
        crate_id = request.POST['crate_id']
        mix = request.FILES.get('mix')
        obj = Crate(
            genre=genre, vibe=vibe, 
            energy_level=energy_level, description=description, 
            crate_id=crate_id, mix=mix)
        obj.save()
        context = {
            'library': library,
        }
        return render(request, 'return_to_crate_database.html', context)
    return redirect('/')

# crate database
def crate_database(request, library_id):
    library = Library.objects.get(id=library_id)

    cartes_to_exclude = [
        'Library to Library',
        'Limbo',
        'On Order',
        'Pending',
        'Processing Order',
        'Stockpile',
        'To Library',
        'En Route',
        'Placing Order',
        'Member',
        'Shipping Requested',
        'Awaiting Payment'
    ]

    _crates = Crate.objects.all()
    other_crates = []
    for crate in cartes_to_exclude:
        c = Crate.objects.get(crate_id=crate)
        other_crates.append(c)
        _crates = _crates.exclude(crate_id__contains=(crate))
    _crates.order_by('crate_id')
    
    p = Paginator(_crates, 50)
    page = request.GET.get('page')
    crates = p.get_page(page)
    nums = "a" * crates.paginator.num_pages

    genres = Genre.objects.all()
    vibes = Vibe.objects.all()
    energy_levels = EnergyLevel.objects.all()

    context = {
        'crates': crates,
        'other_crates': other_crates,
        'library': library,

        'genres': genres,
        'vibes': vibes,
        'energy_levels': energy_levels,

        'nums': nums,
    }
    return render(request,'crate_database.html', context)

# crate database search
def crate_database_search(request, library_id):
    _crates = Crate.objects.all().order_by('crate_id')
    library = Library.objects.get(id=library_id)

    search_crate_id = request.POST['search_crate_id']
    search_genre = request.POST['search_genre']
    search_vibe = request.POST['search_vibe']
    search_energy_level = request.POST['search_energy_level']
    search_description = request.POST['search_description']

    if search_crate_id != 'Crate ID...':
        _crates = _crates.filter(crate_id__exact=(search_crate_id))
    if search_genre != 'Genre...':
        _crates = _crates.filter(genre__exact=(search_genre))
    if search_vibe != 'Vibe...':
        _crates = _crates.filter(vibe__exact=(search_vibe))
    if search_energy_level != 'Energy Level...':
        _crates = _crates.filter(energy_level__exact=(search_energy_level))
    if search_description != 'Search Description...':
        _crates = _crates.filter(description__icontains=(search_description))

    genres = Genre.objects.all()
    vibes = Vibe.objects.all()
    energy_levels = EnergyLevel.objects.all()

    p = Paginator(_crates, 50)
    page = request.GET.get('page')
    crates = p.get_page(page)
    nums = "a" * crates.paginator.num_pages
    
    context = {
        'crates': crates,
        'library': library,

        'search_crate_id': search_crate_id,
        'search_genre': search_genre,
        'search_vibe': search_vibe,
        'search_energy_level': search_energy_level,
        'search_description': search_description,

        'genres': genres,
        'vibes': vibes,
        'energy_levels': energy_levels,

        'nums': nums,
    }
    return render(request,'crate_database.html', context)

# crate delete
def crate_delete(request, library_id, crate_id):
    library = Library.objects.get(id=library_id)
    crate = Crate.objects.get(id=crate_id)
    context = {
        'library': library,
        'crate': crate,
    }
    return render(request,'crate_delete.html', context)

# crate delete submission
def crate_delete_submission(request, library_id, crate_id):
    library = Library.objects.get(id=library_id)
    crate = Crate.objects.get(id=crate_id)
    crate.delete()
    context = {
        'library': library
    }
    return render(request, 'return_to_crate_database.html', context)

# crate edit
def crate_edit(request, library_id, crate_id):
    library = Library.objects.get(id=library_id)
    crate = Crate.objects.get(id=crate_id)
    genres = Genre.objects.all()
    vibes = Vibe.objects.all()
    energy_levels =EnergyLevel.objects.all()
    context = {
        'library': library,
        'crate': crate,

        'genres': genres,
        'vibes': vibes,
        'energy_levels': energy_levels,
    }
    return render(request,'crate_edit.html', context)

# crate edit submission
def crate_edit_submission(request, library_id, crate_id):
    library = Library.objects.get(id=library_id)
    if request.method == 'POST':
        crate = Crate.objects.get(id=crate_id)
        crate.genre = request.POST['genre']
        crate.vibe = request.POST['vibe']
        crate.energy_level = request.POST['energy_level']
        crate.description = request.POST['description']
        crate.crate_id = request.POST['crate_id']
        crate.save()
        context = {
            'library': library
        }
        return render(request, 'return_to_crate_database.html', context)
    return redirect('/')

# return to crate database
def return_to_crate_database(request):
    return render(request, 'return_to_crate_database.html')

############## libraries ##############
def libraries(request):
    libraries = Library.objects.all().order_by('date_established')

    for l in libraries:
        if len(LibraryCrate.objects.filter(library=l)) >= 1:
            l.has_crates = True
    
    context = {
        'libraries':libraries
    }
    return render(request,'libraries.html', context)

# library default crates add
def library_default_crates_add(request, library_id):
    library = Library.objects.get(id=library_id)
    crates_to_add = ['Library to Library', 'Pending']

    for crate in crates_to_add:
        related_crate_id = Crate.objects.get(crate_id__icontains=(crate)).pk
        related_crate__crate_id = Crate.objects.get(crate_id__icontains=(crate)).crate_id
        crate = LibraryCrate(
            related_crate_id = related_crate_id,
            library_id = library_id,
            library_crate_id = str(related_crate__crate_id) + ' ' + str(library.name)[:3].upper(),
            crate_type = crate
        )
        crate.save()

        sub_crate = SubCrate(
            master_library_crate=crate, crate_index_start='A',
            crate_index_end='Z', sub_crate_id=crate.library_crate_id,
            issued='Issued', reserved='Reserved', crate_type='Admin')
        sub_crate.save()

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

        save_barcode(SubCrate.objects.get(id=sub_crate.pk))

    context = {
        'library': library
    }

    return render(request,'return_to_crates.html', context)





############# log in ##############
def log_in(request):
    return render(request,'log_in.html')

def log_in_backend(request):
    if request.method == 'POST':
        login_user_name = request.POST['login_user_name']
        login_password = request.POST['login_password']
        library_user = authenticate(username=login_user_name, password=login_password)
        if library_user is not None:
            login(request, library_user)
            library_user = request.user.id 
    return render(request, 'logged_in.html')

def logged_in(request):
    libraries = Library.objects.all()
    context = {
        'libraries': libraries
    }
    return render(request, 'logged_in.html', context)




############# log out ##############
def log_out(request):
    logout(request)
    return render(request, 'logged_out.html')

def logged_out(request):
    libraries = Library.objects.all()
    context = {
        'libraries': libraries
    }
    return render(request, 'logged_out.html', context)

############# members ##############


############# other ##############
def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/development/development')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})

