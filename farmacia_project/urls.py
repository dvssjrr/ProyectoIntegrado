"""
URL configuration for Farmasur project.
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def redirect_to_inicio(request, exception=None):
    return redirect('inicio')


handler404 = 'farmacia_project.urls.redirect_to_inicio'
handler500 = 'farmacia_project.urls.redirect_to_inicio'

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints - Rutas centralizadas desde farmasur.urls
    path('api/', include('farmasur.urls')),
    # Interfaces web por rol
    path('', include('farmasur.urls.web')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

