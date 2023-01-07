import datetime

import simplejson as json
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from wardrobe.forms import ItemForm, UserPrefsForm, ProfileForm
from wardrobe.models import Item, Category, Outfit, Company, SystemMessage, OutfitWornDate, ItemWornDate, ImageUpload


def index(request):
    user = User.objects.get(username='brandon')
    try:
        item = user.items.order_by('?')[0]
        outfit = user.outfits.order_by('?')[0]
    except:
        item = None
        outfit = None
    return render(request, 'index.html', {'item': item, 'outfit': outfit})


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        next = request.POST.get('next', None)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect(reverse('outfits'))
            else:
                return HttpResponseForbidden('Your account is disabled')
        else:
            return render(request, 'sign_in.html',
                          {'next': next, 'register': settings.REGISTER,
                           'error': True})

    if request.method == "GET":
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('outfits'))
        else:
            next = request.GET.get('next', None)
            return render(request, 'sign_in.html',
                          {'next': next, 'register': settings.REGISTER,
                           'error': False})


@login_required
def edit_profile(request):
    user = request.user
    saved = False
    pw_changed = False
    password_error = None
    form = None
    if request.method == 'GET':
        form = ProfileForm(instance=user.prefs)
    elif request.method == 'POST':
        password = request.POST.get('password', None)
        password2 = request.POST.get('password2', None)
        if password and password2 and password != '':
            if password == password2:
                user.set_password(password)
                user.save()
                pw_changed = True
            else:
                password_error = 'The passwords you entered do not match'
        elif password and not password2:
            password_error = 'You need to confirm your password'
        elif password2 and not password:
            password_error = 'You need to enter both passwords'

        form = ProfileForm(request.POST, instance=user.prefs)
        gender = request.POST['gender']
        birth_year = request.POST['birth_year']
        public_wardrobe = request.POST.get('public_wardrobe', False)
        if public_wardrobe:
            public_wardrobe = True
        saved_gender = user.prefs.gender
        saved_birth_year = user.prefs.birth_year
        saved_public_wardrobe = user.prefs.public_wardrobe
        if gender == saved_gender and birth_year == saved_birth_year and saved_public_wardrobe == public_wardrobe:
            pass
        else:
            if form.is_valid():
                form.save()
                saved = True
    return render(request, 'edit_profile.html',
                  {'form': form, 'saved': saved, 'pw_changed': pw_changed, 'password_error': password_error})


@login_required
def preferences(request):
    user = request.user
    saved = False
    form = None
    if request.method == 'GET':
        form = UserPrefsForm(instance=user.prefs)
    elif request.method == 'POST':
        form = UserPrefsForm(request.POST, instance=user.prefs)
        if form.is_valid():
            form.full_clean()
            form.save()
            request.session['django_timezone'] = user.prefs.time_zone
            saved = True
            if not user.items.all():
                return HttpResponseRedirect(reverse('item_create'))
    return render(request, 'prefs.html',
                  {'form': form, 'saved': saved})


@login_required
def outfits(request):
    user = request.user
    outfits = user.outfits.all()
    if not outfits.exists():
        items = user.items.all()
        if items.exists():
            return HttpResponseRedirect(reverse('outfit_create'))
        else:
            if items.count() < 2:
                return HttpResponseRedirect(reverse('item_create'))
    sys_messages = SystemMessage.objects.all()
    todays_date = user.prefs.get_today()
    first_time = False
    if request.GET.get('first', None):
        first_time = True
    return render(request, 'outfit/list.html',
                  {'outfits': outfits, 'sys_messages': sys_messages,
                   'todays_date': todays_date, 'first_time': first_time})


@login_required
def items(request):
    user = request.user
    items = user.items.all()
    first_time = False
    if request.GET.get('first', None):
        first_time = True
    if not items.exists():
        return HttpResponseRedirect(reverse('item_create'))
    cats = Category.objects.all()
    sys_messages = SystemMessage.objects.all()
    return render(request, 'item/list.html', {
        'items': items, 'cats': cats, 'sys_messages': sys_messages,
        'first_time': first_time})


def public_wardrobe(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    items = user.items.all()
    # if not items.exists():
    cats = Category.objects.all()
    return render(request, 'item/list.html', {
        'puser': user, 'items': items, 'cats': cats})


@login_required
def charts(request):
    user = request.user
    if not user.items.all():
        return HttpResponseRedirect(reverse('item_create'))
    sys_messages = SystemMessage.objects.all()
    cats = Category.objects.all().select_related('parent_category').prefetch_related('items__owner', 'items__company')
    value_cats = []
    count_cats = []
    for cat in cats.iterator():
        if cat.is_top_level():
            count_dict = cat.get_count_dict(user)
            if count_dict:
                count_cats.append(count_dict)
                value_dict = cat.get_value_dict(user)
                if value_dict:
                    value_cats.append(value_dict)

    context = {
        'value_json': json.dumps(value_cats), 'count_json': json.dumps(count_cats),
        'sys_messages': sys_messages
    }
    return render(request, 'charts.html', context)


@login_required
def outfit_create(request):
    user = request.user
    if request.method == 'GET':
        cats = Category.objects.all()
        items = user.items.all()
        if items.count() < 2:
            return HttpResponseRedirect(reverse('item_create'))
        first_time = False
        if request.GET.get('first', None):
            first_time = True
        context = {'cats': cats, 'items': items, 'first_time': first_time}
        return render(request, 'outfit/create.html', context)

    elif request.method == 'POST':
        name = request.POST['name']
        items = request.POST['items']
        image_url = request.POST.get('image-url', None)
        outfit = Outfit(name=name, owner=request.user)
        if image_url:
            outfit.image_url = image_url
        outfit.save()
        for i in items.split(','):
            item = Item.objects.get(id=i)
            outfit.items.add(item)
        return HttpResponse(outfit.id)


@login_required
def outfit_edit(request, outfit_id):
    user = request.user
    outfit = get_object_or_404(Outfit, pk=outfit_id)
    if user != outfit.owner:
        return HttpResponseForbidden('You do not own that outfit.')

    cats = Category.objects.all()
    items = user.items.all()

    if request.method == 'GET':
        context = {'cats': cats, 'items': items, 'outfit': outfit}
        return render(request, 'outfit/create.html', context)

    elif request.method == 'POST':
        name = request.POST['name']
        items = request.POST['items']
        image_url = request.POST.get('image-url', None)
        outfit.name = name
        if image_url:
            outfit.image_url = image_url
        outfit.save()
        outfit.items.clear()
        for i in items.split(','):
            item = Item.objects.get(id=i)
            outfit.items.add(item)
        return HttpResponse(outfit.id)


def outfit_view(request, outfit_id):
    outfit = get_object_or_404(Outfit, pk=outfit_id)
    return render(request, 'outfit/view.html', {'outfit': outfit})


def item_form(request, item_id=None):
    user = request.user
    edit = False
    item = None
    selected_cat = None
    image_uploads = None
    image_uuids = None
    if item_id:
        item = get_object_or_404(Item, pk=item_id)
        selected_cat = item.category
        edit = True
        if user != item.owner:
            return HttpResponseForbidden('You do not own that item.')
    cats = Category.objects.all()
    companies = Company.objects.all()
    if request.method == 'GET':
        if edit:
            image_uploads = item.images.all()
            image_uuids = image_uploads.values_list('uuid')
            if image_uuids:
                image_uuids = image_uuids[0]
                image_uuids = ','.join(str(i) for i in image_uuids)
        form = ItemForm(instance=item, date_format=user.prefs.get_date_format())
        return render(request, 'item/create.html',
                      {'form': form, 'edit': edit, 'cats': cats,
                       'selected_cat': selected_cat, 'image_uploads': image_uploads,
                       'image_uuids': image_uuids})

    elif request.method == 'POST':
        company_name = request.POST.get('company_name', None)
        image_uuids = request.POST.get('image_uuids', None)\
            .replace('[', '')\
            .replace('u\'', '')\
            .replace(']', '')\
            .replace('\'', '')\
            .replace(' ', '')
        if image_uuids:
            image_uploads = []
            if ',' in image_uuids:
                image_uuids = image_uuids.split(',')
                for uuid in image_uuids:
                    iu = ImageUpload.objects.get(uuid=uuid)
                    if not iu.author and not iu.object_id:
                        image_uploads.append(iu)
            else:
                iu = ImageUpload.objects.get(uuid=image_uuids)
                if not iu.author and not iu.object_id:
                    image_uploads.append(iu)
        form = ItemForm(request.POST, instance=item, date_format=user.prefs.get_date_format())
        if form.is_valid():
            item = form.save(commit=False)
            if company_name != '':
                item.company, created = Company.objects.get_or_create(name=company_name)
            item.owner = request.user
            item.save()
            if image_uploads:
                for iu in image_uploads:
                    iu.author = user
                    iu.content_object = item
                    iu.save()
            items = user.items.count()
            if items == 1:
                return HttpResponseRedirect(reverse('items') + '?first=true')
            elif items == 2:
                return HttpResponseRedirect(reverse('outfit_create') + '?first=true')
            else:
                return HttpResponseRedirect(reverse('items'))
        else:
            if request.POST['category']:
                selected_cat = Category.objects.get(id=request.POST['category'])
            else:
                selected_cat = None
            return render(request, 'item/create.html',
                          {'form': form, 'edit': edit, 'cats': cats,
                           'selected_cat': selected_cat, 'image_uuids': image_uuids,
                           'image_uploads': image_uploads})


@login_required
def item_create(request):
    return item_form(request)


@login_required
def item_edit(request, item_id):
    return item_form(request, item_id)


def worn(request):
    user = request.user
    if request.method == "GET":
        if user.is_authenticated:
            cats = Category.objects.all()
            items = Item.objects.filter(owner=user)
            todays_date = user.prefs.get_today()
            context = {'cats': cats, 'items': items, 'todays_date': todays_date}
            return render(request, 'worn.html', context)
        else:
            return HttpResponseRedirect(reverse('item_create') + '?next=/worn/')

    elif request.method == "POST":
        if user.is_authenticated:
            try:
                date = request.POST['date']
            except:
                return HttpResponse(status=406)

            outfit = request.POST.get('outfit', None)
            item_ids = request.POST.get('item_ids', None)
            date_obj = datetime.datetime.strptime(date, user.prefs.get_date_format()).date()
            if outfit:
                outfit_obj = Outfit.objects.get(pk=outfit)
                OutfitWornDate.objects.get_or_create(outfit=outfit_obj, date=date_obj)
                return HttpResponse(status=206)

            elif item_ids:
                item_ids = item_ids.split(',')
                for item_id in item_ids:
                    try:
                        item = Item.objects.get(pk=int(item_id))
                        ItemWornDate.objects.get_or_create(item=item, date=date_obj)
                    except Item.DoesNotExist:
                        return HttpResponse(status=406)
                return HttpResponse(status=206)
            else:
                return HttpResponse(status=406)
        else:
            return HttpResponseForbidden('You must be logged in')


@login_required
def wear_history(request):
    user = request.user

    # Get outfits and items, excluding those with 0 wears
    # Sort by wear count, then latest date worn
    # This logic could be cached for performance

    outfits_temp = user.outfits.all().prefetch_related('dates_worn')
    for outfit in outfits_temp:
        outfit.wear_count = outfit.get_wear_count()
        outfit.last_worn = outfit.get_latest_date_worn()
    outfits = [outfit for outfit in outfits_temp if outfit.wear_count != 0]
    outfits = sorted(outfits, key=lambda o: o.name)
    outfits = sorted(outfits, key=lambda o: o.wear_count, reverse=True)
    outfits = sorted(outfits, key=lambda o: o.last_worn, reverse=True)

    items_temp = user.items.all().prefetch_related('dates_worn')
    for item in items_temp:
        item.wear_count = item.get_wear_count()
        item.last_worn = item.get_latest_date_worn()
    items = [item for item in items_temp if item.wear_count != 0]
    items = sorted(items, key=lambda i: i.name)
    items = sorted(items, key=lambda i: i.wear_count, reverse=True)
    items = sorted(items, key=lambda i: i.last_worn, reverse=True)

    return render(request, 'wear_history.html', {'outfits': outfits, 'items': items})


@login_required
def users_list(request):
    user = request.user
    if not user.is_superuser and not request.impersonator:
        return HttpResponseForbidden('Forbidden')
    else:
        users = list(User.objects.all())
        users = sorted(users, key=lambda u: u.outfits.count(), reverse=True)
        users = sorted(users, key=lambda u: u.items.count(), reverse=True)
        return render(request, 'users_list.html', {'users': users})
