from django.conf.urls import include, url
from django.contrib import admin
from site_app.views import homepage, research_page

urlpatterns = [
    # Examples:
    url(r'^$', homepage, name='home'),
    url(r'^research$', research_page, name='research'),
    url(r'^admin/', include(admin.site.urls)),
]
