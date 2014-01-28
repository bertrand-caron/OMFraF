from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('omfraf.main.views',
    # Examples:
    # url(r'^$', 'omfraf.views.home', name='home'),
    # url(r'^omfraf/', include('omfraf.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'index', name='index'),
    url(r'^generate/$', 'generate', name='generate'),
    url(r'^load/$', 'load', name='load'),
)
