from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'lightshowmaker.views.index', name='index'),
    url(r'^show/(?:([\d])+/)?$', 'lightshowmaker.views.show', name='show'),
    url(r'^show/(\d+)/delete/$', 'lightshowmaker.views.delete_show', name='delete_show'),
    url(r'^show/(\d+)/lights/$', 'lightshowmaker.views.lights', name='lights'),
    url(r'^show/(\d+)/real_time/$', 'lightshowmaker.views.real_time', name='real_time')
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
