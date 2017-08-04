"""
Definition of urls for Bevut.
"""

from django.conf.urls import url
import django.contrib.auth.views

import app.forms
import app.views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', app.views.home, name='home'),
    url(r'^app/$', app.views.courses, name='app_home'),
    url(r'^app/course/$', app.views.courses, name="courses"),
    url(r'^app/course/(?P<id>[0-9]+)/$', app.views.course, name='course'),
    url(r'^app/course/(?P<id>[0-9]+)/actionplans$', app.views.course_action_plan, name='course_action_plan'),
    url(r'^app/form/(?P<id>[0-9]+)/$', app.views.student_form, name='student_form'),
    url(r'^app/form/(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        app.views.readonly_studentform,
        name='readonly_studentform'),
    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'app/login.html'
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]

# vi: ts=4 expandtab
