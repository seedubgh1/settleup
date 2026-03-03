from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# 
from django.views.generic import RedirectView

urlpatterns = [
    # path("", RedirectView.as_view(url="/groups/", permanent=False)),
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("groups/", include("groups.urls")),
    path("alerts/", include("alerts.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
