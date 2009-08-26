from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
        (r'^admin/', include(admin.site.urls)),
        (r'^accounts/', include('registration.urls')),
        (r'^comments/', include('django.contrib.comments.urls')),
        (r'^$', 'bounty.views.index'),
        (r'^new_project', 'bounty.views.new_project'),
        (r'^projects/(?P<project_id>\d+)/$', 'bounty.views.view_project'),
        (r'^projects/(?P<project_id>\d+)/change_status/$',
            'bounty.views.change_project_status'),
        (r'^projects/(?P<project_id>\d+)/donate/$',
            'bounty.views.donate'),
        (r'^projects/$', 'bounty.views.list_projects'),
        (r'^alertpayinstnoti/$', 'bounty.views.donation_notify'),
        (r'^projects/(?P<project_status>pending|accepted)/$',
            'bounty.views.list_projects'),
)

if settings.DEBUG == True:
    urlpatterns += patterns('',
        (r'^static/(.*)$', 'django.views.static.serve', 
            {'document_root': settings.PROJECT_HOME + '/static'}))
