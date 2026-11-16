from django.contrib.auth import views as auth_views
from django.urls import path

from farmasur.views import web

urlpatterns = [
    path('', web.inicio, name='inicio'),
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('panel/admin/', web.panel_admin, name='panel_admin'),
    path('panel/farmaceutico/', web.panel_farmaceutico, name='panel_farmaceutico'),
    path('panel/tecnico/', web.panel_tecnico, name='panel_tecnico'),
    path('panel/bodeguero/', web.panel_bodeguero, name='panel_bodeguero'),
]
