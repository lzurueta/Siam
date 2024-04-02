from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('perfil', login_required(views.ProfileView.as_view()), name="userProfile"),
    # path('abmAlta/<str:app_name>/<str:model_name>/<str:form_name>', login_required(views.abmAlta.as_view()), name="abmAlta"),
    # path('abmEliminar/<str:app_name>/<str:model_name>/<str:form_name>', login_required(views.abmEliminar.as_view()), name="abmEliminar"),
    path('logout_view', login_required(views.logout_view.as_view()), name="logout_view"),
    path('registrarse', views.registerUser, name="registrarUsuario"),
    # path('recuperarConstrasena', views.recuperarConstrasena, name="recuperarConstrasena"),
    path('', login_required(views.home.as_view()), name="home"),
]

