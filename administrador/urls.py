from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path('administracion_usuarios', login_required(views.administracion_usuarios.as_view()),name="administracion_usuarios"),
    path('administracion_usuarios_ajax', login_required(views.administracion_usuarios_ajax.as_view()), name="administracion_usuarios_ajax"),
    path('administracion_usuarios_estado', login_required(views.administracion_usuarios_estado), name="administracion_usuarios_estado"),
    path('administracion_usuarios_actualizar_clave', login_required(views.administracion_usuarios_actualizar_clave),name="administracion_usuarios_actualizar_clave"),

]
