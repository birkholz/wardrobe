import json

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from forms import ImageUploadForm
from models import SystemMessage, Outfit, Item, ImageUpload, UserPrefs


def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"


class JSONResponse(HttpResponse):
    """JSON response class."""

    def __init__(self, obj=None, json_opts=None, mimetype="application/json", *args, **kwargs):
        if obj is None:
            obj = {}
        if json_opts is None:
            json_opts = {}
        content = json.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


def item_delete(request, item_id):
    user = request.user
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return HttpResponse(status=404)

    if item.owner != user:
        return HttpResponse(status=403)
    else:
        item.delete()
        return HttpResponse(status=206)


@login_required
def outfit_delete(request, outfit_id):
    user = request.user
    outfit = get_object_or_404(Outfit, pk=outfit_id)
    if user != outfit.owner:
        return HttpResponseForbidden('You do not own that outfit.')
    else:
        outfit.delete()
        return HttpResponseRedirect(reverse('outfits'))


def read_sys_message(request, msg_id):
    user = request.user
    try:
        msg = SystemMessage.objects.get(pk=msg_id)
    except SystemMessage.DoesNotExist:
        return HttpResponse(status=404)

    msg.users_read.add(user)
    return HttpResponse(status=206)


def sign_out(request):
    logout(request)
    next = request.GET.get('next', None)
    if next:
        return HttpResponseRedirect(next)
    else:
        return HttpResponseRedirect(reverse('login'))


def register(request):
    if settings.REGISTER:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']

            user = User.objects.create_user(username, email, password)
            UserPrefs.objects.create(user=user)
            user2 = authenticate(username=username, password=password)
            login(request, user2)
            return HttpResponseRedirect(reverse('preferences'))
    else:
        return HttpResponseForbidden('Registration is disabled')


def username_check(request):
    username = request.GET['username']
    try:
        User.objects.get(username=username)
        return HttpResponse('no')
    except User.DoesNotExist:
        return HttpResponse('yes')


@csrf_exempt
def image_upload(request):
    user = request.user
    if request.method != 'POST':
        return HttpResponse(status=404)
    else:
        form = ImageUploadForm(request.POST, request.FILES)
        form.author = user
        if form.is_valid():
            iu = form.save()
            item_id = request.GET.get('item_id', None)
            if item_id:
                item = Item.objects.get(id=int(item_id))
                iu.content_object = item
                iu.save()
            f = request.FILES.get('image')
            files = [{
                'url': iu.image.url,
                'name': unicode(iu.uuid),
                "type": "image/png",
                'thumbnailUrl': iu.image.url,
                'size': f.size,
                'deleteUrl': '/image_delete/' + unicode(iu.uuid) + '/',
                'deleteType': "DELETE",
            }]
            data = {"files": files}
            response = JSONResponse(data, {}, response_mimetype(request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response


@csrf_exempt
def image_upload_delete(request, uuid):
    user = request.user
    if request.method != 'POST':
        return HttpResponse(status=404)
    else:
        iu = ImageUpload.objects.get(uuid=uuid)
        if iu.author and iu.author == user:
            iu.delete()
        elif not iu.author:
            iu.delete()
        else:
            return HttpResponse(status=403)
        return HttpResponse(status=206)


def image_upload_list(request):
    user = request.user
    if not user.is_authenticated():
        return HttpResponseForbidden('You must be logged in')
    images = []
    for iu in user.images.iterator():
        images += [{
            'name': iu.image.name,
            'size': iu.image.size,
            'url': iu.image.url,
            'thumbnailUrl': iu.image.url,
            'deleteUrl': reverse('image_delete', args=[iu.uuid]),
            'deleteType': "DELETE"
        }]
    data = {'files': images}
    response = JSONResponse(data, {}, response_mimetype(request))
    response['Content-Disposition'] = 'inline; filename=files.json'
    return response


def set_default_image(request, item_id, uuid):
    user = request.user
    if not user.is_authenticated():
        return HttpResponseForbidden('You must be logged in')
    try:
        item = Item.objects.get(id=item_id)
        iu = ImageUpload.objects.get(pk=uuid)
    except (Item.DoesNotExist, ImageUpload.DoesNotExist):
        return HttpResponse(status=404)
    if user != item.owner:
        return HttpResponseForbidden('You do not own that item')
    if iu.author and iu.author != user:
        return HttpResponseForbidden('You do not own that image')
    iu.content_object = item
    iu.author = user
    item.default_image = iu
    item.save()
    return HttpResponse(status=206)
