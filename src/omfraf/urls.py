from os.path import join
from django.conf.urls import include, url
import omfraf.main.views as views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

RELATIVE_URL = r'^omfraf'

def relative_url(url):
    return join(RELATIVE_URL, url) if bool(url) else RELATIVE_URL

urlpatterns = [
    # Examples:
    # url(r'^$', 'omfraf.views.home', name='home'),
    # url(r'^omfraf/', include('omfraf.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(relative_url(r'$'), views.index, name='index'),
    url(relative_url(r'repos/$'), views.repos, name='repos'),
    url(relative_url(r'generate/$'), views.generate, name='generate'),
    url(relative_url(r'load/$'), views.load, name='load'),
    url(relative_url(r'update_mop/$'), views.update_mop, name='update_mop'),
]
