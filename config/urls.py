from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path(
        "",
        RedirectView.as_view(url="/mailing/mailing/", permanent=False),
        name="root-redirect",
    ),
    path("admin/", admin.site.urls),
    path("mailing/", include("mailing.urls")),
    path("users/", include("users.urls")),
    path("users/", include("django.contrib.auth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
