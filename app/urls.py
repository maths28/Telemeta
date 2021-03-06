# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from django.http import HttpResponse
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('telemeta',),
}

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
robots_rules = open(PROJECT_ROOT + os.sep + 'robots.txt', 'r').read()

urlpatterns = patterns('',
    # Example:
    # (r'^sandbox/', include('sandbox.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/django/', include(admin.site.urls)),
    #(r'^grappelli/', include('grappelli.urls')), # grappelli URLS

    # Telemeta
    (r'^', include('telemeta.urls')),

    # Languages
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^robots\.txt$', lambda r: HttpResponse(robots_rules, mimetype="text/plain")),

    )
