"""
URL configuration for siaf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include

import sistema.views
from siaf import settings

from . import views

urlpatterns = [
    path('', login_required(sistema.views.SistemaHome.as_view()), name="index"),
    path('admin/panel_administrativo', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('sistema/', include('sistema.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('administrador/', include('administrador.urls')),
    path('tablero/', include('tablero.urls')),
    path('prensa/', include('prensa.urls')),
    path('sistema/declaracionJurada', views.enviarDeclaracionJurada, name="enviarDeclaracionJurada"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
