from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import re_path, include
from django.views.generic import TemplateView

from wardrobe import views, ajax

admin.autodiscover()

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^outfit/create/$', views.outfit_create, name='outfit_create'),
    re_path(r'^outfit/(?P<outfit_id>\d+)/$', views.outfit_view, name='outfit_view'),
    re_path(r'^outfit/(?P<outfit_id>\d+)/edit/$', views.outfit_edit, name='outfit_edit'),
    re_path(r'^outfits/$', views.outfits, name='outfits'),
    re_path(r'^item/(?P<item_id>\d+)/edit/$', views.item_edit, name='item_edit'),
    re_path(r'^item/create/$', views.item_create, name='item_create'),
    re_path(r'^items/$', views.items, name='items'),
    re_path(r'^wardrobe/(?P<username>\w+)/$', views.public_wardrobe, name='public_wardrobe'),
    re_path(r'^charts/$', views.charts, name='charts'),
    re_path(r'^sign_in/$', views.login_view, name='login'),
    re_path(r'^worn/$', views.worn, name='worn'),
    re_path(r'^wear_history/$', views.wear_history, name='wear_history'),
    re_path(r'^prefs/$', views.preferences, name='preferences'),
    re_path(r'^profile/$', views.edit_profile, name='edit_profile'),
    re_path(r'^users_list/$', views.users_list, name='users_list'),

    # AJAX views
    re_path(r'^outfit/(?P<outfit_id>\d+)/delete/$', ajax.outfit_delete, name='outfit_delete'),
    re_path(r'^item/(?P<item_id>\d+)/delete/$', ajax.item_delete, name='item_delete'),
    re_path(r'^sign_out/$', ajax.sign_out, name='sign_out'),
    re_path(r'^username_check/$', ajax.username_check, name='username_check'),
    re_path(r'^register/$', ajax.register, name='register'),
    re_path(r'^sysmsg/(?P<msg_id>\d+)/read/$', ajax.read_sys_message, name='read_sys_message'),
    # Images
    re_path(r'^image_upload/$', ajax.image_upload, name='image_upload'),
    re_path(r'^image_upload_list/$', ajax.image_upload_list, name='image_upload_list'),
    re_path(r'^image_upload/(?P<uuid>\w+)/delete/$', ajax.image_upload_delete, name='image_delete'),
    re_path(r'^set_default_image/(?P<item_id>\d+)/(?P<uuid>\w+)/$', ajax.set_default_image,
        name='set_default_image'),

    # Static pages
    re_path(r'^about/$', TemplateView.as_view(template_name="about.html"), name='about'),
    re_path(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    re_path(r'^humans.txt$', TemplateView.as_view(template_name="humans.txt", content_type="text/plain")),

    # Includes
    re_path(r'^impersonate/', include('impersonate.urls')),
    re_path(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static('static/', document_root=settings.STATIC_ROOT)
