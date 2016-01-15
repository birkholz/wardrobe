from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'wardrobe.views.index', name='index'),
    url(r'^outfit/create/$', 'wardrobe.views.outfit_create', name='outfit_create'),
    url(r'^outfit/(?P<outfit_id>\d+)/$', 'wardrobe.views.outfit_view', name='outfit_view'),
    url(r'^outfit/(?P<outfit_id>\d+)/edit/$', 'wardrobe.views.outfit_edit', name='outfit_edit'),
    url(r'^outfits/$', 'wardrobe.views.outfits', name='outfits'),
    url(r'^item/(?P<item_id>\d+)/edit/$', 'wardrobe.views.item_edit', name='item_edit'),
    url(r'^item/create/$', 'wardrobe.views.item_create', name='item_create'),
    url(r'^items/$', 'wardrobe.views.items', name='items'),
    url(r'^wardrobe/(?P<username>\w+)/$', 'wardrobe.views.public_wardrobe', name='public_wardrobe'),
    url(r'^charts/$', 'wardrobe.views.charts', name='charts'),
    url(r'^sign_in/$', 'wardrobe.views.login_view', name='login'),
    url(r'^worn/$', 'wardrobe.views.worn', name='worn'),
    url(r'^wear_history/$', 'wardrobe.views.wear_history', name='wear_history'),
    url(r'^prefs/$', 'wardrobe.views.preferences', name='preferences'),
    url(r'^profile/$', 'wardrobe.views.edit_profile', name='edit_profile'),
    url(r'^users_list/$', 'wardrobe.views.users_list', name='users_list'),

    # AJAX views
    url(r'^outfit/(?P<outfit_id>\d+)/delete/$', 'wardrobe.ajax.outfit_delete', name='outfit_delete'),
    url(r'^item/(?P<item_id>\d+)/delete/$', 'wardrobe.ajax.item_delete', name='item_delete'),
    url(r'^sign_out/$', 'wardrobe.ajax.sign_out', name='sign_out'),
    url(r'^username_check/$', 'wardrobe.ajax.username_check', name='username_check'),
    url(r'^register/$', 'wardrobe.ajax.register', name='register'),
    url(r'^sysmsg/(?P<msg_id>\d+)/read/$', 'wardrobe.ajax.read_sys_message', name='read_sys_message'),
    # Images
    url(r'^image_upload/$', 'wardrobe.ajax.image_upload', name='image_upload'),
    url(r'^image_upload_list/$', 'wardrobe.ajax.image_upload_list', name='image_upload_list'),
    url(r'^image_upload/(?P<uuid>\w+)/delete/$', 'wardrobe.ajax.image_upload_delete', name='image_delete'),
    url(r'^set_default_image/(?P<item_id>\d+)/(?P<uuid>\w+)/$', 'wardrobe.ajax.set_default_image',
        name='set_default_image'),

    # Static pages
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name='about'),
    url(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    url(r'^humans.txt$', TemplateView.as_view(template_name="humans.txt", content_type="text/plain")),

    # Password reset
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset',
        {'template_name': 'auth/password_reset.html', 'from_email': 'notifications@obviously.com',
         'email_template_name': 'email/password_reset_email.html',
         'subject_template_name': 'emails/password_reset_subject.txt'}, name='password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done',
        {'template_name': 'forms-wholepage/password_reset_done.html'}, name='password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'forms-wholepage/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'forms-wholepage/password_reset_complete.html'}, name='password_reset_complete'),

    # Includes
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
