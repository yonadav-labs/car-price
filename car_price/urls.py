from django.conf.urls import url, include

from django.contrib import admin
from project import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.main, name="main"),
    url(r'^(?P<car_name>[^/]+)/$', views.req_brand, name="brand"),
    url(r'^(?P<car_name>[^/]+)/(?P<brand>[^/]+)/$', views.req_year, name="year")
]

