from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 'pmax.views.main_page', name='home'),
                       url(r'pm10', 'pmax.views.powerMaster10_page', name='pm10'),
                       url(r'pm30', 'pmax.views.powerMaster30_page', name='pm30'),
                       url(r'device', 'pmax.views.device_view', name='device_view'),
                       url(r'panel', 'pmax.views.panel_view', name='panel_view'),
                       url(r'ipmpLog', 'pmax.views.ipmp_log_view', name='ipmpLog'),
                       # url(r'^PMTesting/', include('PMTesting.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),
)
