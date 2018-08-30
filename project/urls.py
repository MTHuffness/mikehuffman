from django.conf.urls import include, url
from django.contrib import admin
from site_app.views import homepage

urlpatterns = [
    # Examples:
    url(r'^$', homepage, name='home'),
    url(r'^admin/', include(admin.site.urls)),
]
